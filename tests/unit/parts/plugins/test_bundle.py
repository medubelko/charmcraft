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
import sys


def test_bundleplugin_get_build_package(bundle_plugin):
    assert bundle_plugin.get_build_packages() == set()


def test_bundleplugin_get_build_snaps(bundle_plugin):
    assert bundle_plugin.get_build_snaps() == set()


def test_bundleplugin_get_build_environment(bundle_plugin):
    assert bundle_plugin.get_build_environment() == {}


def test_bundleplugin_get_build_commands(bundle_plugin, tmp_path):
    if sys.platform == "linux":
        assert bundle_plugin.get_build_commands() == [
            f'mkdir -p "{str(tmp_path)}/parts/foo/install"',
            f'cp --archive --link --no-dereference {tmp_path}/parts/foo/build/* "{str(tmp_path)}/parts/foo/install"',
        ]
    else:
        assert bundle_plugin.get_build_commands() == [
            f'mkdir -p "{str(tmp_path)}/parts/foo/install"',
            f'cp -R -p -P {tmp_path}/parts/foo/build/* "{str(tmp_path)}/parts/foo/install"',
        ]
