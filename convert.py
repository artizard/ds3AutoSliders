
def convert(*regions):

    x=y=x2=y2=None
    for i in regions:

        coords = i
        boxCoords = (.061,.149,.453,.705)

        x = (coords[0] - boxCoords[0]) / boxCoords[2]
        y = (coords[1] - boxCoords[1]) / boxCoords[3]
        #x2 = (coords[2] - boxCoords[0]) / boxCoords[2]
        #y2 = (coords[3] - boxCoords[1]) / boxCoords[3]
        print(f"({x:.4f},{y:.4f})",", ",end="",sep="")
       

# convert((.2625,.225),(.3427,.225),(.4234,.225),
#               (.2625,.3657),(.3427,.3657),(.4234,.3657),
#               (.2625,.5019),(.3427,.5019),(.4234,.5019),
#               (.2625,.6389),(.3427,.6389),(.4234,.6389),
#               (.2625,.7731),(.3427,.7731),(.4234,.7731))

convert((.41640625, .2298611111))