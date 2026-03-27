# Proposal

## What will (likely) be the title of your project?

Glitch Machine: Turning Data Slices into Art

## In just a sentence or two, summarize your project. (E.g., "A website that lets you buy and sell stocks.")

A website that lets you import audio files, slices the data, and randomly generates a catchy remix to export. 

## In a paragraph or more, detail your project. What will your software do? What features will it have? How will it be executed?

I will use the PyDub library to slice audio objects, the FFmpeg backend engine to decode and encode mp3 and wav files, as well as the random logic library to create these remixes. The website will be hosted via Streamlit Community Cloud and linked to my Github repository. My workflow will be comrpised of the following steps
    1. Audio Normalization: prompt user's for a source file path, PyDUB will load it and its metadata
    2. Sequential Segmentation: For loop iterates through audio object, user designed variables will slice the audio into smaller segments and each grouping is treated as a data point
    3. Algorithmic Randomization: the random logic library will reorder segments and crossfade them together to avoid dissonant transitions
    4. Rendering and Export: The final shuffled list will be concatenated into a new audio segment and exported as an mp3 file for user downloads

## If planning to combine 1051's final project with another course's final project, with which other course? And which aspect(s) of your proposed project would relate to 1051, and which aspect(s) would relate to the other course?

I do not plan to combine the final project with one for another class

## If planning to collaborate with 1 or 2 classmates for the final project, list their names, email addresses, and the names of their assigned TAs below.

I do not plan to collaborate

## In the world of software, most everything takes longer to implement than you expect. And so it's not uncommon to accomplish less in a fixed amount of time than you hope.

### In a sentence (or list of features), define a GOOD outcome for your final project. I.e., what WILL you accomplish no matter what?

The program successfully imports a local .mp3 file, splices the aduio, randomly shuffles the audio data, and exports a playable audio file

### In a sentence (or list of features), define a BETTER outcome for your final project. I.e., what do you THINK you can accomplish before the final project's deadline?

The program prompts the user for input on how they would like to customize the remixes, polishes remixed audio segments using crossfade, and creates an exportable file

### In a sentence (or list of features), define a BEST outcome for your final project. I.e., what do you HOPE to accomplish before the final project's deadline?

The program is web integrated with Streamilt, uses layering logic to make audio remixes sound catchier, and allows the user to input customize prompts and feedback to create the desired remix

## In a paragraph or more, outline your next steps. What new skills will you need to acquire? What topics will you need to research? If working with one of two classmates, who will do what?

For my next steps, I will start downloading my tech stack and creating a folder for my project. I will ownload FFmpeg binaries and add them to my system's PATH environment variable, before installing PyDub so that I can properly open and export audio files. Next I will simply write code to download an mp3, copy it, and export it, ensuring that my libraries are communicating with my hardware. After this initialization, I will begin drafting my segmentation for loop to slice python audiosegments. Once I have completed the shuffling logic, I can begin working on elevating my project, first adjusting for user input to create their ideal remix, and later by hosting my project with streamlit and integrating the program as a formal web application
This project will allow me to bridge the gap between abstract coding an functional systems, while developing a technical foundation in unstructured data managemenet and alorithmic logic. I will improve my technical skills with Python libraries, specifically PyDub, to manipulate data while gaining hands on experience with API and dependency integration with the FFmpeg engine. I will need to research Digital Signal Processing basic to understand how sampling rates work, as well as randomness to ensure my shuffling algorithms create variety without losing musical cohesion. 