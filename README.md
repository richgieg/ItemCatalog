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
reflect your Google+ / Gmail account, which will give your account
administrative rights on the Music Shop site

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

**Stop the application, exit the SSH session and shutdown the VM:**
```
[press Ctrl+C to stop the application]
exit
vagrant halt
```