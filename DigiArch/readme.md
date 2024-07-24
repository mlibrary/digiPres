# Re-Usable Metadata Form
This form was created in 2024 for the lab to incorporate into our metadata workflow.

## Step 1: Install Node.js
Install [Node.js](https://nodejs.org/en) on the computer that the metadata form will be hosted on.

The installation process should add a pre-built directory to your Desktop (ours is called ExpressProjects).

## Step 2: Edit index.pug and script.js files
Copy and paste the code from index.pug into your own index.pug file that should have been pre-generated. This builds the content of the form; edit as needed to adapt to your needs.

Then, copy script.js into your own javascript folder. This is the script that will turn your form's output into a JSON object and generate a metadata.txt file.

## Step 3: Using the local Node.js server
These next instructions are from the lab's workflow. Some details may be different depending on how your files are named/what system you're using.

1. Open up the ExpressProjects folder in VS Code.
2. In VS Code, open up the terminal by clicking **View -> Terminal** in the top nav bar.
3. In the terminal, type the following commands in order:

```
cd .\Metadata_Form\
npm install
npx cross-env DEBUG=Metadata_Form:* npm start
```

This creates a local server that can be accessed through Chrome which will allow us to see the form and download our metadata.txt file.

4. In Chrome, navigate to localhost:3000 using the search bar. You should see the metadata form!

## Step 4: Closing the server
When done using the metadata form, first click the **Unplug Icon** in VS code then type **Ctrl^C** into the terminal to close the server. You’ll be prompted by the Terminal, enter **‘Y’** then hit **Enter**.

