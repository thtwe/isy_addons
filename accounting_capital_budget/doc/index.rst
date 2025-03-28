User Documentation: Budget Extension (Linux/Windows)
====================================================

| **Company**: `braintec-group <https://www.braintec-group.com/>`_
| **Created on**: 2018/11/06
| **Last changes**: 2018/11/22
| **Last changes by**: Studer Nicola

Introduction
------------

Dear User, thank you for your interest in my `Odoo <https://odoo.com>`_ module! With this
documentation, I’m trying to clear off all questions.

The main objective of this Odoo module is to extend financial reports
with budget information. Create budgets within a fiscal year period. Get
reports with all the accounts and their budgets for a specific time
period.

Module translations available in the following languages:

-  German
-  English
-  French

System Summary
--------------

Odoo specific dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

-  The module uses the `base accounting <https://www.odoo.com/page/accounting>`_ module of the enterprise
   version of Odoo.
-  The module requires the Odoo enterprise version

User Access Levels
~~~~~~~~~~~~~~~~~~

The module uses the same user groups as the base account module:

-  Accountant
-  Advisor

   The group of the user can be changed in the form view of the user
   ``Settings - Users & Companies - User name`` with the field
   ``Application Accesses - Accounting & Finance``

.. image:: access_management.png
   :alt: Access management
   :width: 100 %

Accountant
^^^^^^^^^^

The accountant has rights to **read** the budget informations. The
accountant can’t **write**, **update** or **delete** budgets.

Advisor
^^^^^^^

The advisor has rights to **read**, **write**, **update** and **delete**
budgets.

Getting started
---------------

Bind module variant 1
~~~~~~~~~~~~~~~~~~~~~

1. Open the module in `Odoo Apps <https://apps.odoo.com>`_
2. Click on the download button for your Odoo version
3. Unzip the folder you’ve just downloaded

   1. Linux:

      1. Open a terminal
      2. Move to your download folder ``cd /path/to/download/directory``
      3. If the unzip command isn’t already installed on your system:
         ``sudo apt-get install unzip``
      4. ``unzip budget_extension.zip``

   2. Windows:

      1. Right click on the downloaded zip
      2. Extract files

4. Bind the downloaded module to your odoo-bin script.

   1. Linux:

      1. Move the unzipped folder into the addons directory of odoo
         ``mv /path/to/download/directory/budget_extension /path/to/odoo/addons/``

   2. Windows:

      1. Move the extracted folder to the ``addons`` folder of your Odoo
         installation with the explorer.

5. Restart your Odoo server

Bind module variant 2
~~~~~~~~~~~~~~~~~~~~~

1. Do step 1-3 of the bind module variant 1
2. Start the server with the ``odoo-bin`` script with additional
   parameters

   -  Windows:
      ``python3 odoo-bin -w odoo -r odoo --addons-path=addons,path/to/unzipped/folder/budget_extension``
   -  Linux:
      ``./odoo-bin --addons-path=addons,path/to/unzipped/folder/budget_extension``

Install the module
~~~~~~~~~~~~~~~~~~

1.  Open Odoo in the browser with **active** debug mode
    (``localhost:8069/web?debug=#home``)
2.  Open the ``Apps`` app
3.  Click on the button called ``Update Apps List``

        only visible if the debug mode is activated!

4.  In the new popup click on the button ``update``
5.  Wait until the message "Well done! All your Apps are up-to-date!"
    shows up
6.  Click on the button ``Apps``
7.  Delete the filter in the top right-hand corner
8.  Add "budget_extension" in the search view
9.  Click on the module with the ``$`` sign as icon
10. Click on the blue button ``Install``

Upgrade the module
~~~~~~~~~~~~~~~~~~

Upgrades are needed, if there is an update for a module.

1. Do the steps 6-9 of the "Install the module" section
2. Click on the button ``Upgrade``

Practical usage
---------------

1. Open the ``Accounting`` app as administrator or as advisor
2. Open the register ``Configuration - Extended Budgets``

..

    Note that there is a default filter and "group by" set!


.. image:: Menu_Item.png
   :alt: Menu Item
   :width: 100 %



Field descriptions
~~~~~~~~~~~~~~~~~~

.. image:: fields.png
   :alt: Fields
   :width: 100 %

= ============== ===================================================
# Field          Description
= ============== ===================================================
1 Title          Name of the budget to distinguish them
2 Account        Account for the budget
3 Planned Amount Amount that should be earned or maximum expenditure
4 Start Date     Start date of the budget period
5 End Date       End date of the budget period
= ============== ===================================================

Create an extended budget
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Click on the button ``Create`` in the top left-hand corner
2. **Before** you choose the **name** of your budget, choose an account
3. After you've chosen your account, the recommended budget name, start
   date and end date should be filled in automatically
4. Enter a planned amount for the budget
5. Save the budget with the green button ``Save`` in the top left-hand
   corner

..

   You can even try to give it a name before you choose the account. Try
   for example the name ``3600 Budget 2018`` and you should see, that
   the account, the start date and end date are filled in automatically

Duplicate a budget
~~~~~~~~~~~~~~~~~~

1. Click on the budget you want to copy
2. Click on the button called ``Actions`` in the top middle of the
   screen
3. Choose the option ``Duplicate``
4. Make the changes
5. Save it

..

   Note that the start and end date have changed to the next possible
   date range within a fiscal year

Delete a budget
~~~~~~~~~~~~~~~

1. Click on the budget you want to delete
2. Click on the button called ``Actions`` in the top middle of the
   screen
3. Choose the option ``Delete``
4. In the popup click on the button ``OK`` to accept the deletion

Save the budgets
~~~~~~~~~~~~~~~~

If you don't want to loose your budget data, it's highly recommended to
save your budgets in a local file.

1. Remove all filters and all group by's in the top right-hand corner
2. Click on the little box on the left of the column ``Budget Name``

      If you don't want to save all of the budgets, uncheck the boxes on
      the left of the budgets

3. Click on the button called ``Actions`` in the top middle of the
   screen
4. Choose the option ``Export``
5. Doubleclick all **underlined** fields on the left
6. Choose a file type that works for you (e.g. "Excel")
7. Click on the button ``Expoert to file`` in the bottom left-hand
   corner
8. Move the file to a save place

Restore the budgets
~~~~~~~~~~~~~~~~~~~

This procedure depends on the file you've created in the section "Save
the budgets"

1. Click on the button ``Import`` in the top left-hand corner
2. Load the file with your backup data
3. Click on the button ``Test Import`` in the top left-hand corner

      If everything is OK you should get the message "Everything seems
      valid"

4. Click on the button ``Import`` in the top left-hand corner
5. Check if the budgets were created

Use filters
~~~~~~~~~~~

1. Click on the button ``Filters`` in the top right-hand corner
2. Enable the wanted filter

.. image:: filters.png
   :alt: Filters
   :width: 100 %

=================== =========================================================================================
Filter              Description
=================== =========================================================================================
This fiscal year    Searches all of the budgets that have their start and end date in the current fiscal year
Past fiscal years   Searches all of the budgets that have their start and end date in the past fiscal years
Future fiscal years Searches all of the budgets that have their start and end date in the future fiscal years
=================== =========================================================================================

..

   You can use more than one filter at the same time!

Use diagrams to get a general idea of your budgets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diagrams are pretty useful if you use them to show someone your budget
configuration or you want to compare the budgets.

1. Click on the diagram button in the top right-hand corner
2. Choose the diagram type you want in the top left-hand corner
3. Play a bit with all of the settings

Show the budgets in a financial report
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open a financial report (e.g. ``Reporting - Profit and Loss``)
2. Click on the button ``Comparison`` in the top right-hand corner
3. Choose the Budget Comparison
4. Check the new created columns with the automatically filled in values

.. image:: enable_comparison.png
   :alt: Enable Comparison
   :width: 100 %

..

   The export as .xslx file and the print as pdf works just fine with
   this module! Check it out!

Restrictions
------------

There are few restrictions, which are important make the module works!

-  The fiscal year of the start date and end date **must** be identical
-  The end date must be **subsequent** to the start date
-  The time period should be unique and shouldn't overlap another budget
   with the same account


Appendix
--------

Change the fiscal year date
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Open the tab ``Configuration - Settings`` of the ``Accounting`` app
2. Go to the section "Fiscal Periods"
3. Change the values of the field ``Last Day``

      Attention, the Odoo core doesn't handle invalid dates until
      version 12!