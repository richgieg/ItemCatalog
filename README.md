# Item Catalog

This is the third project in my pursuit of the Full-Stack Web Developer
Nanodegree from Udacity. Following is Udacity's description for this project:

"In this project, you will be developing a web application that provides a list
of items within a variety of categories and integrate third party user
registration and authentication. Authenticated users should have the ability to
post, edit, and delete their own items. You will be creating this project
essentially from scratch, no templates have been provided for you. This means
that you have free reign over the HTML, the CSS, and the files that include the
application itself utilizing Flask."

To execute this project, please follow the steps in the sections below.

----
## Install VirtualBox 4.3
VirtualBox 4.3 is required for Vagrant to function. The steps for installing it
vary depending on your operating system. You can find the installer for many
operating systems [here](https://www.virtualbox.org/wiki/Download_Old_Builds_4_3).

If you happen to be using Ubuntu 15.04 (as I did for this project), you can try
this terminal command:
```
sudo apt-get install virtualbox-4.3
```

*This command will probably work for other versions of Ubuntu as well.*

----
## Install Vagrant
Vagrant is required to manage the virtual machine (VM) used for executing this
project. The VM image is automatically fetched by Vagrant when the VM is
powered up the first time. The VM comes preconfigured with Python and
PostgreSQL. The steps for installing Vagrant vary depending on your operating
system. You can find the installer for many operating systems
[here](https://www.vagrantup.com/downloads.html).

If you happen to be using Ubuntu 15.04 (as I did for this project), you can try
this terminal command:
```
sudo apt-get install vagrant
```

*This command will probably work for other versions of Ubuntu as well.*

----
## Run the Application
Use a command line terminal for the following steps.

**Clone the repository to your local system, then launch the VM:**
```
git clone https://github.com/richgieg/ItemCatalog.git
cd ItemCatalog/vagrant
vagrant up
```

*It may take several minutes for the VM to spin up when you're launching it for
the first time, since the VM image is being fetched and the one-time
configuration must take place. Please be patient. Once the process is complete,
your terminal prompt will be returned, thus allowing you to execute the next
steps.*

**Add yourself as site administrator:**

1. Open ```seed.py``` in your favorite editor

2. Edit the "email" field of the dictionary literal in the global USERS list to
reflect your Google+ / Gmail account (replacing musicshop999), which will give
your account administrative rights on the Music Shop site when you sign in

**Connect to the VM via SSH, seed the database, then run the application:**
```
vagrant ssh
cd /vagrant
python seed.py
python application.py
```

**Navigate to the following URL in your browser:**
```
http://localhost:8000
```


**Authenticate:**

- Use the red Google+ sign-in button at the top of the page


**Add a new item:**

1. Navigate to the category in which you'd like to add a new item

2. Click the "New Item" button near the top of the page

3. Fill out the form appropriately and click "Save"


**Edit an existing item:**

1. Navigate to the item you would like to edit

2. Click the "Edit" button

3. Fill out the form appropriately and click "Save"


**Delete an existing item:**

1. Navigate to the item you would like to delete

2. Click the "Delete" button

3. Answer the confirmation prompt


**User Management:**

When a new user signs in, an account will be created but will have read-only
access to the site until approved by an administrator. When logged in as
an account with administrator privileges, you will see a "User Management"
navigation link. This page will allow you to change a user account from
read-only access to either standard or administrator. Standard accounts can
create new items. They can also edit or delete items they created. Administrator
accounts can create new items and edit or delete any item on the site. If a
standard user has created items, but gets demoted to read-only, they will no
longer have the ability to edit or delete the items they created.


**View JSON dump for all items:**
```
http://localhost:8000/catalog.json
```


**View JSON dump for all items in a category:**
```
http://localhost:8000/guitars.json
```
*The word "guitars" can be replaced with any valid category.*


**View JSON dump for a single item:**
```
http://localhost:8000/guitars/epiphone-pr-150-acoustic-guitar.json
```
*The word "guitars" can be replaced with any valid category and
"epiphone-pr-150-acoustic-guitar" can be replaced with any valid item in the
specified category.*


**View XML dump for all items:**
```
http://localhost:8000/catalog.xml
```

**View XML dump for all items in a category:**
```
http://localhost:8000/guitars.xml
```
*The word "guitars" can be replaced with any valid category.*


**View XML dump for a single item:**
```
http://localhost:8000/guitars/epiphone-pr-150-acoustic-guitar.xml
```
*The word "guitars" can be replaced with any valid category and
"epiphone-pr-150-acoustic-guitar" can be replaced with any valid item in the
specified category.*


**Stop the application, exit the SSH session and shutdown the VM:**
```
[press Ctrl+C to stop the application]
exit
vagrant halt
```
