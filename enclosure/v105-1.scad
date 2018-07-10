
/*//////////////////////////////////////////////////////////////////
              -    FB Aka Heartman/Hearty 2016     -                   
              -   http://heartygfx.blogspot.com    -                  
              -       OpenScad Parametric Box      -                     
              -         CC BY-NC 3.0 License       -                      
////////////////////////////////////////////////////////////////////                                                                                                             
12/02/2016 - Fixed minor bug 
28/02/2016 - Added holes ventilation option                    
09/03/2016 - Added PCB feet support, fixed the shell artefact on export mode. 
21/11/2017 by Richard Pillay - Added ability to have up to 4 PCBs

*/////////////////////////// - Info - //////////////////////////////

// All coordinates are starting as integrated circuit pins.
// From the top view :

//   CoordD           <---       CoordC
//                                 ^
//                                 ^
//                                 ^
//   CoordA           --->       CoordB


////////////////////////////////////////////////////////////////////


////////// - Paramètres de la boite - Box parameters - /////////////

/* [Box dimensions] */
// - Longueur - Length  
  Length        = 105;       
// - Largeur - Width
  Width         = 85;                     
// - Hauteur - Height  
  Height        = 40;  
// - Epaisseur - Wall thickness  
  Thick         = 2;//[2:5]  
  
/* [Box options] */
// - Diamètre Coin arrondi - Filet diameter  
  Filet         = 4;//[0.1:12] 
// - lissage de l'arrondi - Filet smoothness  
  Resolution    = 4;//[1:100] 
// - Tolérance - Tolerance (Panel/rails gap)
  m             = 0.9;
// Pieds PCB - PCB feet (x4 for each) 
  PCB01Feet       = 1;// [0:No, 1:Yes]
  PCB02Feet       = 0;// [0:No, 1:Yes]
  PCB03Feet       = 0;// [0:No, 1:Yes]
  PCB04Feet       = 0;// [0:No, 1:Yes]
// - Decorations to ventilation holes
  Vent          = 1;// [0:No, 1:Yes]
// - Decoration-Holes width (in mm)
  Vent_width    = 1.5;   


  
/* [PCB_Feet] */
//All dimensions are from the center foot axis

PCB01Text = "     Pi Zero W";
// - Coin bas gauche - Low left corner X position
PCB01PosX         = 0;
// - Coin bas gauche - Low left corner Y position
PCB01PosY         = 2;
// - Longueur PCB01 - PCB01 Length
PCB01Length       = 23;
// - Largeur PCB01 - PCB01 Width
PCB01Width        = 58;
// - Heuteur pied - Feet height
PCB01FootHeight      = 5;
// - Diamètre pied - Foot diameter
PCB01FootDiam         = 6;
// - Diamètre trou - Hole diameter
PCB01FootHole        = 2.5;  

PCB02Text = "PMS";
PCB02PosX           = 35;
PCB02PosY           = 6;
PCB02Length         = 38;
PCB02Width          = 50;
PCB02FootHeight     = 5;
PCB02FootDiam      = 4;
PCB02FootHole        = 2;  
  
PCB03Text = "PCB3";
PCB03PosX           = 95;
PCB03PosY         = 84;
PCB03Length       = 50;
PCB03Width        = 55;
PCB03FootHeight      = 10;
PCB03FootDiam         = 8;
PCB03FootHole        = 3;  
  
PCB04Text = "PCB4";
PCB04PosX         = 75;
PCB04PosY         = 6;
PCB04Length       = 70;
PCB04Width        = 50;
PCB04FootHeight      = 10;
PCB04FootDiam         = 8;
PCB04FootHole        = 3;  
  

/* [STL element to export] */
//Coque haut - Top shell
TShell          = 0;// [0:No, 1:Yes]
//Coque bas- Bottom shell
BShell          = 0;// [0:No, 1:Yes]
//Panneau avant - Front panel
FPanL           = 1;// [0:No, 1:Yes]
//Panneau arrière - Back panel  
BPanL           = 1;// [0:No, 1:Yes]


  
/* [Hidden] */
// - Couleur coque - Shell color  
Couleur1        = "Orange";       
// - Couleur panneaux - Panels color    
Couleur2        = "OrangeRed";    
// Thick X 2 - making decorations thicker if it is a vent to make sure they go through shell
Dec_Thick       = Vent ? Thick*2 : Thick; 
// - Depth decoration
Dec_size        = Vent ? Thick*2 : 0.8;


/////////// - Boitier générique bord arrondis - Generic rounded box - //////////

module RoundBox($a=Length, $b=Width, $c=Height){// Cube bords arrondis
                    $fn=Resolution;            
                    translate([0,Filet,Filet]){  
                    minkowski (){                                              
                        cube ([$a-(Length/2),$b-(2*Filet),$c-(2*Filet)], center = false);
                        rotate([0,90,0]){    
                        cylinder(r=Filet,h=Length/2, center = false);
                            } 
                        }
                    }
                }// End of RoundBox Module

      
////////////////////////////////// - Module Coque/Shell - //////////////////////////////////         

module Coque(){//Coque - Shell  
    Thick = Thick*2;  
    difference(){    
        difference(){//sides decoration
            union(){    
                     difference() {//soustraction de la forme centrale - Substraction Fileted box
                      
                        difference(){//soustraction cube median - Median cube slicer
                            union() {//union               
                            difference(){//Coque    
                                RoundBox();
                                translate([Thick/2,Thick/2,Thick/2]){     
                                        RoundBox($a=Length-Thick, $b=Width-Thick, $c=Height-Thick);
                                        }
                                        }//Fin diff Coque                            
                                difference(){//largeur Rails        
                                     translate([Thick+m,Thick/2,Thick/2]){// Rails
                                          RoundBox($a=Length-((2*Thick)+(2*m)), $b=Width-Thick, $c=Height-(Thick*2));
                                                          }//fin Rails
                                     translate([((Thick+m/2)*1.55),Thick/2,Thick/2+0.1]){ // +0.1 added to avoid the artefact
                                          RoundBox($a=Length-((Thick*3)+2*m), $b=Width-Thick, $c=Height-Thick);
                                                    }           
                                                }//Fin largeur Rails
                                    }//Fin union                                   
                               translate([-Thick,-Thick,Height/2]){// Cube à soustraire
                                    cube ([Length+100, Width+100, Height], center=false);
                                            }                                            
                                      }//fin soustraction cube median - End Median cube slicer
                               translate([-Thick/2,Thick,Thick]){// Forme de soustraction centrale 
                                    RoundBox($a=Length+Thick, $b=Width-Thick*2, $c=Height-Thick);       
                                    }                          
                                }                                          


                difference(){// wall fixation box legs
                    union(){
                        translate([3*Thick +5,Thick,Height/2]){
                            rotate([90,0,0]){
                                    $fn=6;
                                    cylinder(d=16,Thick/2);
                                    }   
                            }
                            
                       translate([Length-((3*Thick)+5),Thick,Height/2]){
                            rotate([90,0,0]){
                                    $fn=6;
                                    cylinder(d=16,Thick/2);
                                    }   
                            }

                        }
                            translate([4,Thick+Filet,Height/2-57]){   
                             rotate([45,0,0]){
                                   cube([Length,40,40]);    
                                  }
                           }
                           translate([0,-(Thick*1.46),Height/2]){
                                cube([Length,Thick*2,10]);
                           }
                    } //Fin fixation box legs
            }

        union(){// outbox sides decorations
            
            for(i=[0:Thick:Length/4]){

                // Ventilation holes part code submitted by Ettie - Thanks ;) 
                    translate([10+i,-Dec_Thick+Dec_size,1]){
                    cube([Vent_width,Dec_Thick,Height/4]);
                    }
                    translate([(Length-10) - i,-Dec_Thick+Dec_size,1]){
                    cube([Vent_width,Dec_Thick,Height/4]);
                    }
                    translate([(Length-10) - i,Width-Dec_size,1]){
                    cube([Vent_width,Dec_Thick,Height/4]);
                    }
                    translate([10+i,Width-Dec_size,1]){
                    cube([Vent_width,Dec_Thick,Height/4]);
                    }
  
                
                    }// fin de for
               // }
                }//fin union decoration
            }//fin difference decoration


            union(){ //sides holes
                $fn=50;
                translate([3*Thick+5,20,Height/2+4]){
                    rotate([90,0,0]){
                    cylinder(d=2,20);
                    }
                }
                translate([Length-((3*Thick)+5),20,Height/2+4]){
                    rotate([90,0,0]){
                    cylinder(d=2,20);
                    }
                }
                translate([3*Thick+5,Width+5,Height/2-4]){
                    rotate([90,0,0]){
                    cylinder(d=2,20);
                    }
                }
                translate([Length-((3*Thick)+5),Width+5,Height/2-4]){
                    rotate([90,0,0]){
                    cylinder(d=2,20);
                    }
                }
            }//fin de sides holes

        }//fin de difference holes
}// fin coque 

////////////////////////////// - Experiment - ///////////////////////////////////////////





/////////////////////// - Foot with base filet - /////////////////////////////
module foot(FootDia,FootHole,FootHeight){
    Filet=2;
    color(Couleur1)   
    translate([0,0,Filet-1.5])
    //translate([(Thick*3)+(FootDia/2)+(Filet/2)+m,(Thick)+(FootDia/2)+(Filet/2),Thick])
    difference(){
    
    difference(){
            //translate ([0,0,-Thick]){
                cylinder(d=FootDia+Filet,FootHeight-Thick, $fn=100);
                        //}
                    rotate_extrude($fn=100){
                            translate([(FootDia+Filet*2)/2,Filet,0]){
                                    minkowski(){
                                            //square(10);
                                            square(FootHeight-Filet);
                                            circle(Filet, $fn=100);
                                        }
                                 }
                           }
                   }
            cylinder(d=FootHole,FootHeight+1, $fn=Resolution);
               }          
}// Fin module foot
  
module Feet(PCBText, Length, Width, FootHeight, FootDiam, FootHole){     
//////////////////// - PCB only visible in the preview mode - /////////////////////    
    translate([3*Thick+2,Thick+5,FootHeight+(Thick/2)-0.5]){
    
    %square ([Length+10,Width+10]);
       translate([Length/2,Width/2,0.5]){ 
        color("Olive")
        %text(PCBText, halign="center", valign="center", font="Arial black", size=4);
       }
    } // Fin PCB 
  
    
////////////////////////////// - 4 Feet - //////////////////////////////////////////     
    translate([3*Thick+7,Thick+10,Thick/2]){
        foot(FootDiam, FootHole, FootHeight);
    }
    translate([(3*Thick)+Length+7,Thick+10,Thick/2]){
        foot(FootDiam, FootHole, FootHeight);
        }
    translate([(3*Thick)+Length+7,(Thick)+Width+10,Thick/2]){
        foot(FootDiam, FootHole, FootHeight);
        }        
    translate([3*Thick+7,(Thick)+Width+10,Thick/2]){
        foot(FootDiam, FootHole, FootHeight);
    }   

} // Fin du module Feet
 




 
 ////////////////////////////////////////////////////////////////////////
////////////////////// <- Holes Panel Manager -> ///////////////////////
////////////////////////////////////////////////////////////////////////

//                           <- Panel ->  
module Panel(Length,Width,Thick,Filet){
    scale([0.5,1,1])
    minkowski(){
            cube([Thick,Width-(Thick*2+Filet*2+m),Height-(Thick*2+Filet*2+m)]);
            translate([0,Filet,Filet])
            rotate([0,90,0])
            cylinder(r=Filet,h=Thick, $fn=Resolution);
      }
}



//                          <- Circle hole -> 
// Cx=Cylinder X position | Cy=Cylinder Y position | Cdia= Cylinder dia | Cheight=Cyl height
module CylinderHole(OnOff,Cx,Cy,Cdia){
    if(OnOff==1)
    translate([Cx,Cy,-1])
        cylinder(d=Cdia,10, $fn=50);
}
//                          <- Square hole ->  
// Sx=Square X position | Sy=Square Y position | Sl= Square Length | Sw=Square Width | Filet = Round corner
module SquareHole(OnOff,Sx,Sy,Sl,Sw,Filet){
    if(OnOff==1)
     minkowski(){
        translate([Sx+Filet/2,Sy+Filet/2,-1])
            cube([Sl-Filet,Sw-Filet,10]);
            cylinder(d=Filet,h=10, $fn=Resolution);
       }
}


 
//                      <- Linear text panel -> 
module LText(OnOff,Tx,Ty,Font,Size,Content){
    if(OnOff==1)
    translate([Tx,Ty,Thick+.5])
    linear_extrude(height = 0.5){
    text(Content, size=Size, font=Font);
    }
}
//                     <- Circular text panel->  
module CText(OnOff,Tx,Ty,Font,Size,TxtRadius,Angl,Turn,Content){ 
      if(OnOff==1) {
      Angle = -Angl / len(Content);
      translate([Tx,Ty,Thick+.5])
          for (i= [0:len(Content)-1] ){   
              rotate([0,0,i*Angle+90+Turn])
              translate([0,TxtRadius,0]) {
                linear_extrude(height = 0.5){
                text(Content[i], font = Font, size = Size,  valign ="baseline", halign ="center");
                    }
                }   
             }
      }
}
////////////////////// <- New module Panel -> //////////////////////
module BPanL(){
    difference(){
        color(Couleur2)
        Panel(Length,Width,Thick,Filet);
    
 
    rotate([90, 0, 90]){
        color(Couleur2){
//                     <- Cutting shapes from here ->  
        SquareHole  (0,20,20,15,10,1); //(On/Off, Xpos,Ypos,Length,Width,Filet)
        SquareHole  (0,40,20,15,10,1);
        SquareHole  (1, 5, 4,1.5,Height - 14,0); 
        SquareHole  (1, 8, 4,1.5,Height - 14,0);             
        SquareHole  (1,11, 4,1.5,Height - 14,0);
        SquareHole  (1,14, 4,1.5,Height - 14,0);
        SquareHole  (1,17, 4,1.5,Height - 14,0);
        SquareHole  (1,20, 4,1.5,Height - 14,0);
        SquareHole  (1,23, 4,1.5,Height - 14,0);
        SquareHole  (1,26, 4,1.5,Height - 14,0);
        SquareHole  (1,29, 4,1.5,Height - 14,0);
        SquareHole  (1,32, 4,1.5,Height - 14,0);
        SquareHole  (1,35, 4,1.5,Height - 14,0);            
        //SquareHole  (1,(Length - 50), -1,20,10,0);
        SquareHole  (1,(Width-35), -1,20,10,0);
        CylinderHole(0,27,40,8);       //(On/Off, Xpos, Ypos, Diameter)
        CylinderHole(0,47,40,8);
        CylinderHole(0,67,40,8);
        SquareHole  (0,20,50,80,30,3);
        CylinderHole(0,93,30,10);
        SquareHole  (0,120,20,30,60,3);
//                            <- To here -> 
           }
       }
}

    color(Couleur1){
        translate ([-.5,0,0])
        rotate([90,0,90]){
//                      <- Adding text from here ->          
        LText(0,20,83,"Arial Black",4,"Digital Screen");//(On/Off, Xpos, Ypos, "Font", Size, "Text")
        LText(0,120,83,"Arial Black",4,"Level");
        LText(0,20,11,"Arial Black",6,"  1     2      3");
        CText(0,93,29,"Arial Black",4,10,180,0,"1 . 2 . 3 . 4 . 5 . 6");//(On/Off, Xpos, Ypos, "Font", Size, Diameter, Arc(Deg), Starting Angle(Deg),"Text")
//                            <- To here ->
            }
      }
}

module FPanL(){
    difference(){
        color(Couleur2)
        Panel(Length,Width,Thick,Filet);
    
 
    rotate([90,0,90]){
        color(Couleur2){
//                     <- Cutting shapes from here ->  
        SquareHole  (0,20,20,15,10,1); //(On/Off, Xpos,Ypos,Length,Width,Filet)
        SquareHole  (1, 5, 4,1.5,Height - 14,0); 
        SquareHole  (1, 8, 4,1.5,Height - 14,0);             
        SquareHole  (1,11, 4,1.5,Height - 14,0);
        SquareHole  (1,14, 4,1.5,Height - 14,0);
        SquareHole  (1,17, 4,1.5,Height - 14,0);
        SquareHole  (1,20, 4,1.5,Height - 14,0);
        SquareHole  (1,23, 4,1.5,Height - 14,0);
        SquareHole  (1,26, 4,1.5,Height - 14,0);
        SquareHole  (1,29, 4,1.5,Height - 14,0);
        SquareHole  (1,32, 4,1.5,Height - 14,0);
        SquareHole  (1,35, 4,1.5,Height - 14,0);           
        SquareHole  (1,38, 4,1.5,Height - 14,0);           
        SquareHole  (1,41, 4,1.5,Height - 14,0);           
        SquareHole  (1,44, 4,1.5,Height - 14,0);           
        SquareHole  (1,47, 4,1.5,Height - 14,0);           
        SquareHole  (1,50, 4,1.5,Height - 14,0);                      
        SquareHole  (1,53, 4,1.5,Height - 14,0); 
        SquareHole  (1,56, 4,1.5,Height - 14,0); 
        SquareHole  (1,59, 4,1.5,Height - 14,0); 
        SquareHole  (1,62, 4,1.5,Height - 14,0); 
        SquareHole  (1,65, 4,1.5,Height - 14,0);         
        SquareHole  (1,68, 4,1.5,Height - 14,0);         
        SquareHole  (1,71, 4,1.5,Height - 14,0);         
        SquareHole  (1,74, 4,1.5,Height - 14,0);         
        //SquareHole  (1,(Length - 45), -1,15,11,0);
        
        CylinderHole(0,27,40,8);       //(On/Off, Xpos, Ypos, Diameter)
        CylinderHole(0,47,40,8);
        CylinderHole(0,67,40,8);
        SquareHole  (0,20,50,80,30,3);
        CylinderHole(0,93,30,10);
        SquareHole  (0,120,20,30,60,3);
//                            <- To here -> 
           }
       }
}

    color(Couleur1){
        translate ([-.5,0,0])
        rotate([90,0,90]){
//                      <- Adding text from here ->          
        LText(0,20,83,"Arial Black",4,"Digital Screen");//(On/Off, Xpos, Ypos, "Font", Size, "Text")
        LText(0,120,83,"Arial Black",4,"Level");
        LText(0,20,11,"Arial Black",6,"  1     2      3");
        CText(0,93,29,"Arial Black",4,10,180,0,"1 . 2 . 3 . 4 . 5 . 6");//(On/Off, Xpos, Ypos, "Font", Size, Diameter, Arc(Deg), Starting Angle(Deg),"Text")
//                            <- To here ->
            }
      }
}

/////////////////////////// <- Main part -> /////////////////////////

if(TShell==1)
// Coque haut - Top Shell
        color( Couleur1,1){
            translate([0,Width,Height+0.2]){
                rotate([0,180,180]){
                        Coque();
                        }
                }
        }

if(BShell==1)
// Coque bas - Bottom shell
        color(Couleur1){ 
        Coque();
        }

// Pied support PCB01 - PCB01 feet
if (BShell==1 && PCB01Feet==1)
// Feet
        translate([PCB01PosX,PCB01PosY,0]){ 
            Feet(PCB01Text, PCB01Length, PCB01Width, PCB01FootHeight, PCB01FootDiam, PCB01FootHole);     
        }

if (BShell==1 && PCB02Feet==1)
// Feet
        translate([PCB02PosX,PCB02PosY,0]){ 
            Feet(PCB02Text, PCB02Length, PCB02Width, PCB02FootHeight, PCB02FootDiam, PCB02FootHole);     
        }

if (BShell==1 && PCB03Feet==1)
// Feet
        translate([PCB03PosX,PCB03PosY,0]){ 
            Feet(PCB03Text, PCB03Length, PCB03Width, PCB03FootHeight, PCB03FootDiam, PCB03FootHole);     
        }

if (BShell==1 && PCB04Feet==1)
// Feet
        translate([PCB04PosX,PCB04PosY,0]){ 
            Feet(PCB04Text, PCB04Length, PCB04Width, PCB04FootHeight, PCB04FootDiam, PCB04FootHole);     
        }

// Panneau avant - Front panel  <<<<<< Text and holes only on this one.
//rotate([0,-90,-90]) 
if(FPanL==1)
        translate([Length-(Thick*2+m/2),Thick+m/2,Thick+m/2])
        FPanL();

//Panneau arrière - Back panel
if(BPanL==1)
        color(Couleur2)
        translate([Thick+m/2,Thick+m/2,Thick+m/2])
        //Panel(Length,Width,Thick,Filet);
        BPanL();