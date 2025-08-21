
def convert(*regions):

    x=y=x2=y2=None
    for i in regions:

        coords = i
        boxCoords = (.061,.149,.453,.705)

        x = (coords[0] - boxCoords[0]) / boxCoords[2]
        y = (coords[1] - boxCoords[1]) / boxCoords[3]
        x2 = (coords[2] - boxCoords[0]) / boxCoords[2]
        y2 = (coords[3] - boxCoords[1]) / boxCoords[3]
        print(f"({x:.4f},{y:.4f},{x2:.4f},{y2:.4f})",",",end="",sep="")
       

convert((.494,.738,.521,.761))

# convert((0.13984375,0.21666666),(0.13984375,0.2625),(0.13984375,0.30902777),
#         (0.13984375,0.35555555),(0.13984375,0.40138888),(0.13984375,0.4479166),
#         (0.13984375,0.49444444),(0.13984375,0.21666666))