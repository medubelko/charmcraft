# Copyright 2023 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For further info, check https://github.com/canonical/charmcraft
"""craft-application based lifecycle commands."""

from __future__ import annotations

import pathlib
import textwrap
from typing import TYPE_CHECKING, Any, cast

import craft_cli
from craft_application.commands import lifecycle
from craft_cli import ArgumentParsingError, CraftError
from typing_extensions import override

from charmcraft import models, services, utils

if TYPE_CHECKING:  # pragma: no cover
    import argparse

BUNDLE_MANDATORY_FILES = ["bundle.yaml", "README.md"]


def get_lifecycle_commands() -> list[type[craft_cli.BaseCommand]]:
    """Return the lifecycle related command group."""
    return [
        lifecycle.CleanCommand,
        lifecycle.PullCommand,
        lifecycle.BuildCommand,
        lifecycle.StageCommand,
        lifecycle.PrimeCommand,
        PackCommand,
    ]


class PackCommand(lifecycle.PackCommand):
    """Command to pack the final artifact."""

    name = "pack"
    help_msg = "Build the charm or bundle"
    overview = textwrap.dedent(
        """
        Build and pack a charm operator package or a bundle.

        You can `juju deploy` the resulting `.charm` or bundle's `.zip`
        file directly, or upload it to Charmhub with `charmcraft upload`.

        For the charm you must be inside a charm directory with a valid
        `metadata.yaml`, `requirements.txt` including the `ops` package
        for the Python operator framework, and an operator entrypoint,
        usually `src/charm.py`.  See `charmcraft init` to create a
        template charm directory structure.

        For the bundle you must already have a `bundle.yaml` (can be
        generated by Juju) and a README.md file.
        """
    )

    @override
    def _fill_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._fill_parser(parser)

        parser.add_argument(
            "--bases-index",
            action="append",
            type=int,
            help="Index of 'bases' configuration to build (can be used multiple "
            "times); zero-based, defaults to all",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force packing even after finding lint errors",
        )
        parser.add_argument(
            "--measure",
            type=pathlib.Path,
            help="Dump measurements to the specified file",
        )
        include_charm_group = parser.add_mutually_exclusive_group()
        include_charm_group.add_argument(
            "--include-all-charms",
            action="store_true",
            help="For bundles, pack all charms whose source is inside the bundle directory",
        )
        include_charm_group.add_argument(
            "--include-charm",
            action="append",
            type=pathlib.Path,
            help="For bundles, pack the charm in the referenced path. Can be used multiple times",
        )
        parser.add_argument(
            "--output-bundle",
            type=pathlib.Path,
            help="Write the bundle configuration to this path",
        )
        parser.add_argument(
            "--format",
            choices=["json"],
            help="Produce a machine-readable format (currently only json)",
        )
        parser.add_argument(
            "--project-dir",
            "-p",
            type=pathlib.Path,
            default=pathlib.Path.cwd(),
            help="Specify the project's directory (defaults to current)",
        )

    @override
    @staticmethod
    def _should_add_shell_args() -> bool:
        return True

    def _validate_args(self, parsed_args: argparse.Namespace) -> None:
        project = cast(models.CharmcraftProject, self._services.project)
        package_service = cast(services.PackageService, self._services.package)
        if project.type == "charm":
            if parsed_args.include_all_charms:
                raise ArgumentParsingError(
                    "--include-all-charms can only be used when packing a bundle. "
                    f"Currently trying to pack: {package_service.project_dir}"
                )
            if parsed_args.include_charm:
                raise ArgumentParsingError(
                    "--include-charm can only be used when packing a bundle. "
                    f"Currently trying to pack: {package_service.project_dir}"
                )
            if parsed_args.output_bundle:
                raise ArgumentParsingError(
                    "--output-bundle can only be used when packing a bundle. "
                    f"Currently trying to pack: {package_service.project_dir}"
                )

    def _validate_bases_indices(self, bases_indices):
        """Validate that bases index is valid."""
        if bases_indices is None:
            return

        project = cast(models.Charm, self._services.project)

        msg = "Bases index '{}' is invalid (must be >= 0 and fit in configured bases)."
        len_configured_bases = len(project.bases)
        for bases_index in bases_indices:
            if bases_index < 0:
                raise CraftError(msg.format(bases_index))
            if bases_index >= len_configured_bases:
                raise CraftError(msg.format(bases_index))

    def _update_charm_libs(self) -> None:
        """Update charm libs attached to the project."""
        craft_cli.emit.progress(
            "Checking that charmlibs match 'charmcraft.yaml' values"
        )
        project = cast(models.CharmcraftProject, self._services.project)
        libs_svc = cast(services.CharmLibsService, self._services.charm_libs)
        installable_libs: list[models.CharmLib] = []
        for lib in project.charm_libs:
            library_name = utils.QualifiedLibraryName.from_string(lib.lib)
            if not libs_svc.get_local_version(
                charm_name=library_name.charm_name, lib_name=library_name.lib_name
            ):
                installable_libs.append(lib)
        if installable_libs:
            store = cast(services.StoreService, self._services.store)
            libraries_md = store.get_libraries_metadata(installable_libs)
            with craft_cli.emit.progress_bar(
                "Downloading charmlibs...", len(installable_libs)
            ) as progress:
                for library in libraries_md:
                    craft_cli.emit.debug(repr(library))
                    lib_contents = store.get_library(
                        library.charm_name,
                        library_id=library.lib_id,
                        api=library.api,
                        patch=library.patch,
                    )
                    libs_svc.write(lib_contents)
                    progress.advance(1)

    def _run(
        self,
        parsed_args: argparse.Namespace,
        step_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._validate_args(parsed_args)

        project = cast(models.CharmcraftProject, self._services.project)
        if project.charm_libs:
            self._update_charm_libs()

        return super()._run(parsed_args, step_name, **kwargs)
