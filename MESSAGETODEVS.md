I've decided to open source this project, but as a fair warning, this code is pretty messy, and is not well documented. I had planned on refactoring and documenting this code before releasing it, but honestly I just want to get this project out, so I can work on other things. I debated whether or not to open source it because of this, but ultimately I figured it was for the best to go open source. If anyone reading this decides to modify/improve this project and has any questions, feel free to message me and I'll do my best to help out. (contact info on main page)\
\
I provided a requirements.txt file for the dependencies, and I used Python 3.10.6 for this. \
\
One main technical issue with this project that's worth noting, is the input validation. I created a system detect and handle missed inputs, which allows this program to work regardless of fps, however it slows down this program a fair amount. This is primarily because I have it set to wait 5 frames after each input (this doesn't apply to actually setting the sliders). This was kind of a bandaid fix to my system, and this absolutely can be improved, however I am so burnt out on this project that I'm just leaving it as is. \
\
The main issues that need fixing are:
1. input validation
2. import/export does not work for rosaria's rebirth
3. import always tries to start after 5 seconds from pressing start, it would be better for it to wait until the game is ready, then start 