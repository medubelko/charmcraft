.. _manage-12-factor-app-charms:

Manage a 12-factor app charm
============================

These guides walk you through all ways you can manage 12-factor app charms,
from initialization to usage.

:ref:`Extensions <profile>` add customized elements to a charm for specific
web app frameworks. While the overall basic logic is the same as
:ref:`managing a charm <manage-charms>`, the following guides are about
the 12-factor app charm workflow.

Initialization
--------------

You need both a rock and a charm to have a deployable 12-factor app in Juju.

The charm initialization step uses the ``--profile`` flag to cater the initial
charm files for your specific framework.

.. toctree::
   :maxdepth: 2

   Initialize your 12-factor app charm <init-web-app-charm>

Configuration
-------------

Once your 12-factor app charm has been set up, you can customize many aspects
of it using Juju.

.. toctree::
   :maxdepth: 2

   Configure your 12-factor app charm <configure-web-app-charm>

Integration
-----------

Once deployed, your 12-factor app can be integrated into nearly anything in the
Juju ecosystem.

.. toctree::
   :maxdepth: 2

   Integrate your 12-factor app charm <integrate-web-app-charm>

Usage
-----

Now that you've initialized and configured your 12-factor app charm, you're
ready to use it.


.. toctree::
   :maxdepth: 2

   Use your 12-factor app charm <use-web-app-charm>

