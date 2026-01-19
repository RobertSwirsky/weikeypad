include <YAPPgenerator_v3.scad>


pcbLength     = 95.250;
pcbWidth      = 47.0;
pcbThickness  =  2;

lidWallHeight  = 10;
baseWallHeight = 15;

wallThickness = 3;
ridgeHeight = 6.0;

standoffHeight           = 10.0;
standoffPinDiameter      = 2.0;
standoffHoleSlack     = 0.5;
standoffDiameter         = 8;

paddingFront = 30;
paddingBack  = 30;
paddingRight = 4;
paddingLeft  = 4;

showOrientation = false;

//  *** Snap Joins ***
XsnapJoins   =   
[
    [6, 5, yappLeft, yappRight]
   ,[pcbLength-6, 5, yappLeft, yappRight]
];


connectors   =  
[
    [12, 12, standoffHeight
     , 2.7           //-- diameter of the screw (add some slack)
     , 5             //-- the diameter of the screw head
     , 4.1           //-- the diameter of the insert
     , 9             //-- the outside diameter of the connector
     , yappCoordBox, yappThroughLid],
   [ 12, pcbWidth + paddingRight -1, standoffHeight
     , 2.7           //-- diameter of the screw (add some slack)
     , 5             //-- the diameter of the screw head
     , 4.1           //-- the diameter of the insert
     , 9             //-- the outside diameter of the connector
     , yappCoordBox,yappThroughLid],
   [ pcbLength + paddingFront + paddingBack -6, pcbWidth + paddingRight -2,standoffHeight
     , 2.7           //-- diameter of the screw (add some slack)
     , 5             //-- the diameter of the screw head
     , 4.1           //-- the diameter of the insert
     , 9             //-- the outside diameter of the connector
     , yappCoordBox, yappThroughLid],
   [ pcbLength + paddingFront + paddingBack - 6, 12, standoffHeight,
     , 2.7           //-- diameter of the screw (add some slack)
     , 5             //-- the diameter of the screw head
     , 4.1           //-- the diameter of the insert
     , 9             //-- the outside diameter of the connector
     , yappCoordBox,yappThroughLid],
     //-- use [0,0,0] of the PCB os origen //-- use [0,0,0] of the PCB os origen
];

pcbStands = [
  [ 5, 5, yappBaseOnly, yappHole  ], 
  [ 87.5 + 5, 39 + 5, yappBaseOnly, yappHole  ],   
  [ 5, 39+5, yappBaseOnly, yappHole   ],  
  [ 87.5 + 5, 5, yappBaseOnly, yappHole  ] 
];

cutoutsBack =   
[
    [ (pcbWidth  ) / 2, 0,
      10, 7, 0, yappRectangle, yappCenter]
];

cutoutsFront =   
[
    [ (pcbWidth  ) / 2, 0,
      10, 7, 0, yappRectangle, yappCenter]
];


// Default origin for boxMounts is yappCoordBox: box[0,0,0]
boxMounts =
[
//  [13, 3, 3, 3, yappLeft, yappRight, yappFront, yappBack]
    [paddingFront, 5, -5, 4, yappLeft, yappRight, yappCenter],
    [pcbLength  + paddingFront, 5, -5, 4, yappLeft, yappRight, yappCenter]
];

YAPPgenerate();
