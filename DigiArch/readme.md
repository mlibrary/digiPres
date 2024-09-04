# Re-Usable Metadata Form
This form was created in 2024 for the U-M Digital Preservation Lab to incorporate into our metadata workflow.

The form is compatible with Google Chrome, Microsoft Edge, Mozilla Firefox, Safari, and Opera. For more specific version info, please reference [this link](https://www.w3schools.com/tags/att_a_download.asp).

## Step 1: Install Node.js (note: these instructions are written for a Windows machine)
Instructions adapted and synthesized from [Installing Node.js on Windows](https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-windows) and [Node.js tutorial in Visual Studio Code](https://code.visualstudio.com/docs/nodejs/nodejs-tutorial).

### Download and install Node.js
1. Download the [**nvm-setup.zip**](https://github.com/coreybutler/nvm-windows/releases) file for the most recent release.
2. Once downloaded, open the zip file and run the **nvm-setup.exe** file.
3. The Setup-NVM-for-Windows installation wizard will walk you through the setup steps, including choosing the directory where both nvm-windows and Node.js will be installed.
   
![Screenshot of Setup-NVM-for-Windows installation GUI](https://learn.microsoft.com/en-us/windows/images/install-nvm-for-windows-wizard.png)

4. Once the installation is complete. Open PowerShell (recommend opening with elevated Admin permissions) and try using windows-nvm to list which versions of Node are currently installed (should be none at this point): ```nvm ls```

![Screenshot of terminal when nvm ls command is run](https://learn.microsoft.com/en-us/windows/images/windows-nvm-powershell-no-node.png)

6. Install the latest stable LTS release of Node.js (recommended) by first looking up what the current LTS version number is with: ```nvm list available```, then installing the LTS version number with: ```nvm install <version>``` (replacing <version> with the number, ie: nvm install 12.14.0).

![Screenshot of list of nvm versions available](https://learn.microsoft.com/en-us/windows/images/windows-nvm-list.png)

7. List what versions of Node are installed: ```nvm ls```. Now you should see the version that you just installed listed.

![Screenshot of Node versions installed](https://github.com/user-attachments/assets/a553d254-3a80-4db3-8c65-d7a191c02e1c)

9. Select this version to use by entering: ```nvm use <version>``` (replacing <version> with the number, ie: nvm use 12.9.0).

### Creating metadata form app directory in VS code
10. In the PowerShell, ```cd``` into Desktop.
11. Run the command ```npm install -g express-generator```. The ```-g``` switch installs the Express Generator globally on your machine so you can run it from anywhere.
12. We can now scaffold a new Express application for our metadata form by running: ```express Metadata_Form --view pug```. This creates a new folder on your Desktop called ```Metadata_Form``` with the contents of your application.

![Screenshot of terminal output after running express command](https://github.com/user-attachments/assets/b60b8165-8fc1-4771-a664-ad06069160c1)

14. Open the **Metadata_Form** directory in VS Code.

## Step 2: Edit index.pug and script.js files
1. Copy and paste the code from [index.pug](https://github.com/mlibrary/digiPres/blob/main/DigiArch/views/index.pug) into your own generated **index.pug** file. This builds the content of the form; edit as needed to adapt to your needs.

![Screenshot of new index.pug content pasted in](https://github.com/user-attachments/assets/bbed45a6-8760-4bef-b80c-9dbcf69ff698)

3. Then, download and add [script.js](https://github.com/mlibrary/digiPres/blob/main/DigiArch/public/javascripts/script.js) into your own **public -> javascripts** folder. This is the code that will turn your form's output into a JSON object and generate a metadata.txt file.

![Screenshot of script.js in pubic/javascripts folder](https://github.com/user-attachments/assets/4be73353-5131-405e-b3de-50d1b03c0122)

## Step 3: Using the local Node.js server
These next instructions are from the lab's workflow. Some details may be different depending on how your files are named/what system you're using.

1. Open up the **Metadata_Form** folder in VS Code.
2. In VS Code, open up the terminal by clicking **View -> Terminal** in the top nav bar.
3. In the terminal, type the following commands in order:

```
cd .\Metadata_Form\
npm install
npx cross-env DEBUG=Metadata_Form:* npm start
```

This creates a local server that can be accessed through a browser which will allow us to see the form and download our metadata.txt file.

![Screenshot of terminal output when the above commands are run](https://github.com/user-attachments/assets/23d640b3-8f0e-4646-9ed4-e40ebd4655b2)

4. In a browser, navigate to **localhost:3000** using the search bar. You should see the metadata form!

![Screenshot of metadata form in Chrome browser](https://github.com/user-attachments/assets/4c2b6de9-502a-460f-9706-7b3c8e4ab3d7)

## Step 3.5: Re-routing file downloads in browser
Default browser settings will typically send any downloads to your local machine's Downloads folder; however, since we want these metadata.txt files to land in a specific bag, I suggest changing your browser's settings to turn the **"Always ask where to save files"** option on.

![Screenshot of browser settings that allow user to decide where a downloaded file will go](https://github.com/user-attachments/assets/a8293723-1e0f-409f-a5a3-232303eea768)

## Step 4: Using the metadata form
1. Once the metadata form is open, fill in any relevant fields (if a field is N/A, just leave it blank).
2. When all fields are filled out, click **Submit**.
3. You'll be prompted by your browser to choose where the file should go. Enter the desired pathway then hit **Enter**.

Congrats, you now have a metadata text file that follows Archivematica (and XML) standards!

## Step 4: Closing the server
When done using the metadata form, type **Ctrl^C** into the VS Code terminal to close the server. You’ll be prompted by the terminal, enter **‘Y’** then hit **Enter**.

