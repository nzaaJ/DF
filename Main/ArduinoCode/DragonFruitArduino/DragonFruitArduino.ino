#define ButtonStart (4)
#define PusherHome_LS (5)
#define Sorter1Home_LS (7)
#define Sorter2Home_LS (6)
#define LED1 (26)
#define LED2 (28)
// #define Sorter1Forward_LS (24)
// #define Sorter2Forward_LS (28)
#define ButtonStop (3)
#define Buzzer (42)
#define LED (48)

#include <NewPing.h>2
NewPing Sonar1(8, 10, 200);
NewPing Sonar2(8, 9, 200);
NewPing Sonar3(8, 11, 200);
float d1;
float d2;
float d3;
float DistanceThreshold = 10;
int PushMillis = 18000;

#include "HX711.h"
HX711 cell(A14, A15);
float weight = 0;
float WeightThreshold = 0.1; //For detection
float WeightAccept = 0.3; //if less than, REJECTED

#define Motor (3)
#define Dispenser_Pin (24)
#define PusherForward_Pin (32)
#define PusherHome_Pin (30)
#define Sorter1Forward_Pin (36)
#define Sorter1Home_Pin (34)
#define Sorter2Forward_Pin (40)
#define Sorter2Home_Pin (38)
#define Conveyor_Pin (22)

#include <millisDelay.h>
millisDelay Timer1;
millisDelay Timer2;
millisDelay TimerA;

#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27,20,4);

void setup() {
    Serial.begin(9600); 
    //Buttons
    pinMode(ButtonStart, INPUT_PULLUP);
    // pinMode(Sorter1Forward_LS, INPUT_PULLUP);
    // pinMode(Sorter2Forward_LS, INPUT_PULLUP);
    pinMode(PusherHome_LS, INPUT);
    pinMode(Sorter1Home_LS, INPUT);
    pinMode(Sorter2Home_LS, INPUT);

    //Relays
    // pinMode(Motor, OUTPUT); digitalWrite(Motor, HIGH);
    pinMode(Dispenser_Pin, OUTPUT); digitalWrite(Dispenser_Pin, HIGH);
    pinMode(PusherForward_Pin, OUTPUT); digitalWrite(PusherForward_Pin, HIGH);
    pinMode(PusherHome_Pin, OUTPUT); digitalWrite(PusherHome_Pin, HIGH);
    pinMode(Sorter1Forward_Pin, OUTPUT); digitalWrite(Sorter1Forward_Pin, HIGH);
    pinMode(Sorter1Home_Pin, OUTPUT); digitalWrite(Sorter1Home_Pin, HIGH);
    pinMode(Sorter2Forward_Pin, OUTPUT); digitalWrite(Sorter2Forward_Pin, HIGH);
    pinMode(Sorter2Home_Pin, OUTPUT); digitalWrite(Sorter2Home_Pin, HIGH);
    pinMode(Conveyor_Pin, OUTPUT); digitalWrite(Conveyor_Pin, HIGH);
    pinMode(LED1, OUTPUT); digitalWrite(LED1, HIGH);
    pinMode(LED2, OUTPUT); digitalWrite(LED2, HIGH);
    pinMode(Buzzer, OUTPUT); digitalWrite(Buzzer, HIGH);
    pinMode(ButtonStop, INPUT);
    attachInterrupt(digitalPinToInterrupt(ButtonStop), Stopping, FALLING);
    lcd.init();
    lcd.backlight();

    cell.set_scale(18100); //for calibration
    cell.tare(); //reset

    LCDprint(0, 0, "  WAITING FOR RPI  ");
    LCDprint(0, 1, "     CONNECTION    ");
    int p = 0; TimerA.start(1000);
    while (1) {
        if (TimerA.justFinished()) {
            if (p == 0) {p=1; LCDprint(8, 2, ".   "); TimerA.start(1000);}
        else if (p == 1) {p=2; LCDprint(8, 2, ".."); TimerA.start(1000);}
        else if (p == 2) {p=3; LCDprint(8, 2, "..."); TimerA.start(1000);}
        else if (p == 3) {p=0; LCDprint(8, 2, "...."); TimerA.start(1000);}
        }
        if (Serial.available()) {break;}
    } // displays dot for every second while arduino is loading

    while (0) {
        weight = cell.get_units();
        Serial.println(String(weight,2) + " g");
        delay(500);
    }

    while (0) {
        // Serial.print(digitalRead(Sorter1Forward_LS));
        // Serial.print(digitalRead(Sorter2Forward_LS));
        Serial.print(digitalRead(PusherHome_LS));
        Serial.print(digitalRead(Sorter1Home_LS));
        Serial.println(digitalRead(Sorter2Home_LS));
    } // Prints the status of the pusher and sorters

    while (0) {
        d1 = Sonar1.ping_cm(); delay(30); // delay of 0.03 seconds
        d2 = Sonar2.ping_cm(); delay(30);
        d3 = Sonar3.ping_cm(); delay(30);
        Serial.print("D1:");
        Serial.print(d1);
        Serial.print("  D2:");
        Serial.print(d2);
        Serial.print("  D3:");
        Serial.println(d3);
    }
    LCDprint(0, 0, "   ACTUATORS HOME  ");
    LCDprint(0, 1, "                   ");
    LCDprint(0, 2, "                   ");
    LCDprint(0, 3, "                   ");
    HomeAll();
    LCDprint(0,0,"Premium:            ");
    LCDprint(0,1,"Class A:            ");
    LCDprint(0,2,"Rejected:           ");
    LCDprint(0,3,"weight:             ");
}

char receivedChar;
int Premiums;
int Classas;
int Rejecteds;
int ToStop = 0;

void Stopping() {
    delay(100);
    if (digitalRead(ButtonStop)==LOW) {
        ToStop = 1;
//        Serial.println("Stop");
    }
} // turns off arduino

int First_Time = 1;
int USDetection = 1;
void loop() {
    // Serial.println("LOOP");
//    Serial.print(digitalRead(PusherHome_LS));
//    Serial.print(digitalRead(Sorter1Home_LS));
//    Serial.println(digitalRead(Sorter2Home_LS));
    if (Serial.available()) {
        receivedChar = Serial.read(); //Data received from Raspi in form of string
             if (receivedChar == '1') {ToggleLH(500, PusherForward_Pin);}
        else if (receivedChar == '2') {ToggleLH(500, PusherHome_Pin);}
        else if (receivedChar == '3') {ToggleLH(500, Sorter1Forward_Pin);}
        else if (receivedChar == '4') {ToggleLH(500, Sorter1Home_Pin);}
        else if (receivedChar == '5') {ToggleLH(500, Sorter2Forward_Pin);}
        else if (receivedChar == '6') {ToggleLH(500, Sorter2Home_Pin);}
        else if (receivedChar == '7') {ToggleLH(4000, Conveyor_Pin);}
        else if (receivedChar == '8') {ToggleLH(500, Dispenser_Pin);}
        else if (receivedChar == '9') {Dispense();}
        else if (receivedChar == 'A') {PusherForward();}
        else if (receivedChar == 'B') {Sorter1Forward();}
        else if (receivedChar == 'C') {Sorter2Forward();}
        else if (receivedChar == 'D') {Conveyor_Function();}
        else if (receivedChar == 'E') {RelayLOWwithLimit(Sorter1Home_Pin,Sorter1Home_LS);}
        else if (receivedChar == 'F') {RelayLOWwithLimit(Sorter2Home_Pin,Sorter2Home_LS);}
        else if (receivedChar == 'G') {RelayLOWwithLimit(PusherHome_Pin,PusherHome_LS);}
        else if (receivedChar == 'H') {Sorter2Forward();}
        else if (receivedChar == 'I') {digitalWrite(LED1, LOW);}
        else if (receivedChar == 'J') {digitalWrite(LED1, HIGH);}
        else if (receivedChar == 'K') {digitalWrite(LED2, LOW);}
        else if (receivedChar == 'L') {digitalWrite(LED2, HIGH);}
        else if (receivedChar == 'M') {digitalWrite(Buzzer, LOW);}
        else if (receivedChar == 'N') {digitalWrite(Buzzer, HIGH);}
        else if (receivedChar == 'Z') {
            int RTime = 30;
            while (1) {
                
                LCDprint(0, 0, " SHUTTING DOWN RPI ");
                LCDprint(0, 1, "         " + String(RTime) + "         ");
                LCDprint(0, 2, "                   ");
                LCDprint(0, 3, "                   ");
                if (RTime == 0) {
                    LCDprint(0, 0, "    YOU CAN NOW    ");
                    LCDprint(0, 1, "      TURN THE     ");
                    LCDprint(0, 2, "    SWITCH OFF.    ");
                    LCDprint(0, 3, "                   ");
                    break;
                  }
                delay(1000);
                RTime--;
                
            }
        }
        // else if (receivedChar == '6') {Sorter1();}
        // else if (receivedChar == '7') {Sorter2();}
    }
    
    if ((digitalRead(ButtonStart) == LOW)) {
        ToStop = 0;
        // while (1) {
        //     Serial.print('B'); // rpi ito
        //     delay(10000);
        //     if (ToStop == 1) {Serial.println("Broken"); break;}
        // }
        LCDprint(0,0,"Premium: 0          ");
        LCDprint(0,1,"Class A: 0          ");
        LCDprint(0,2,"Rejected: 0         ");
        LCDprint(0,3,"weight: 0           ");
//        Serial.println("Started");
        digitalWrite(LED1, LOW);
        digitalWrite(LED2, LOW);
        
        Dispense(); delay(1000);

        while (1) {

            weight = cell.get_units(); //TO IDENTIFY IF REJECT
            while (Serial.available()) {receivedChar = Serial.read();}
            LCDprint(0,3,"weight: " + String(weight,2)+ " g    ");
            if (weight > WeightAccept) {Serial.print('A');} //ASKS THE RPI WHAT QUALITY IT HAS
            else {Serial.print('B');} //TELLS THE RPI IT IS REJECTED BY WEIGHT and NO NEED TO CLASSIFY
            receivedChar = ' ';
            
            while (1) { //WAITS FOR RPI'S REPLY
                if (Serial.available()) {
                    receivedChar = Serial.read();
                    if (receivedChar == '4') {
                        digitalWrite(Buzzer,LOW); delay(5000);
                        digitalWrite(Buzzer,HIGH);
                        receivedChar = '3';
                        Rejecteds--;
                    }
                    break;
                }
            }

            PusherForward();
            Conveyor_Function();

            if (receivedChar == '1') {
                Premiums++;
                LCDprint(0,0,"Premium: " + String(Premiums) + "    ");
                Sorter1Forward();
            }
            if (receivedChar == '2') {
                Classas++;
                LCDprint(0,1,"Class A: " + String(Classas) + "    ");
                Sorter2Forward();
            }
            if (receivedChar == '3') {
                Rejecteds++;
                LCDprint(0,2,"Rejected: " + String(Rejecteds) + "    ");
                while (1) {
                    if (digitalRead(PusherHome_LS)==LOW) {digitalWrite(PusherHome_Pin, HIGH); break;}
                }
                Dispense();
            }

            First_Time = 0;
            if (ToStop == 1) {
                digitalWrite(Dispenser_Pin, HIGH);
                digitalWrite(LED1, HIGH);
                digitalWrite(LED2, HIGH);
                HomeAll();
                break;}
//            break;
        }
    }
    receivedChar = ' ';
}

//FUNCTIONS

void HomeAll() {                
    RelayLOWwithLimit(Sorter1Home_Pin,Sorter1Home_LS);
    RelayLOWwithLimit(Sorter2Home_Pin,Sorter2Home_LS);
    RelayLOWwithLimit(PusherHome_Pin,PusherHome_LS);
}
void Dispense() { //You raise me up the dragon fruit
    digitalWrite(Dispenser_Pin, LOW); delay(50);
    while (1) {
        if (ToStop == 1) {break;}
        weight = cell.get_units();
        if (weight < 0) {weight = 0;}
        LCDprint(0,3,"weight: " + String(weight,2)+ " g    ");
        if (weight > WeightThreshold) {break;}
    } delay(500);
    weight = cell.get_units();
    digitalWrite(Dispenser_Pin, HIGH);
}
void PusherForward() {
    digitalWrite(PusherForward_Pin, LOW); delay(50);//PUSHES THE DRAGONFRUIT
    if (First_Time == 0) {
        if (digitalRead(Sorter1Home_LS)==HIGH) {digitalWrite(Sorter1Home_Pin, LOW); delay(50);}
        if (digitalRead(Sorter2Home_LS)==HIGH) {digitalWrite(Sorter2Home_Pin, LOW); delay(50);}
    }  
    
    Timer1.start(7000);
    while (1) {
      if (digitalRead(Sorter1Home_LS)==LOW) {digitalWrite(Sorter1Home_Pin, HIGH);}
       if (digitalRead(Sorter2Home_LS)==LOW) {digitalWrite(Sorter2Home_Pin, HIGH);}
      if (Timer1.justFinished()) {break;}
      }
      
    digitalWrite(PusherForward_Pin, HIGH); delay(50);
    int done1 = 0;
    int done2 = 0;
    while(1) {
        if (digitalRead(Sorter1Home_LS)==LOW) {digitalWrite(Sorter1Home_Pin, HIGH); done1 = 1;}
        if (digitalRead(Sorter2Home_LS)==LOW) {digitalWrite(Sorter2Home_Pin, HIGH); done2 = 1;}
        if ((done1==1) && (done2==1)) {break;}
      }
    delay(1000);

    if (receivedChar == '3') {
        digitalWrite(PusherHome_Pin, LOW); 
    }
}

void Sorter1Forward() {
    digitalWrite(PusherHome_Pin, LOW); 
    digitalWrite(Sorter1Forward_Pin, LOW); delay(50);
    int done1 = 0;
    int done2 = 0;
    int done3 = 0;
    Timer1.start(PushMillis);
    while (1) {
        if (Timer1.justFinished()) {digitalWrite(Sorter1Forward_Pin, HIGH); done1 = 1;}
        if (done2==0) {
            if (digitalRead(PusherHome_LS)==LOW) {digitalWrite(PusherHome_Pin, HIGH); 
            if (ToStop==0) {digitalWrite(Dispenser_Pin, LOW);} 
            delay(50); done2 = 1;}
          }
        if (ToStop==1) {digitalWrite(Dispenser_Pin, HIGH); done3=1;}
        if (done2==1) {
            weight = cell.get_units();
            if (weight < 0) {weight = 0;}
            LCDprint(0,3,"weight: " + String(weight,2)+ " g    ");
            if (weight > WeightThreshold) {digitalWrite(Dispenser_Pin, HIGH); done3=1;}
          }
        if ((done1==1) && (done2==1) && (done3==1)) {break;}
    }
}

void Sorter2Forward() {
    digitalWrite(PusherHome_Pin, LOW); 
    digitalWrite(Sorter2Forward_Pin, LOW); delay(50);
    int done1 = 0;
    int done2 = 0;
    int done3 = 0;
    Timer1.start(PushMillis);
    while (1) {
        if (Timer1.justFinished()) {digitalWrite(Sorter2Forward_Pin, HIGH); done1 = 1;}
        if (done2==0) {
            if (digitalRead(PusherHome_LS)==LOW) {digitalWrite(PusherHome_Pin, HIGH); 
            if (ToStop==0) {digitalWrite(Dispenser_Pin, LOW);} 
            delay(50); done2 = 1;}
          }
        if (ToStop==1) {digitalWrite(Dispenser_Pin, HIGH); done3=1;}
        if (done2==1) {
            weight = cell.get_units();
            if (weight < 0) {weight = 0;}
            LCDprint(0,3,"weight: " + String(weight,2)+ " g    ");
            if (weight > WeightThreshold) {digitalWrite(Dispenser_Pin, HIGH); done3=1;}
          }
        if ((done1==1) && (done2==1) && (done3==1)) {break;}
    }
}

void Conveyor_Function() {
  digitalWrite(Conveyor_Pin, LOW); 
            if (receivedChar == '1') {Timer1.start(2600);} //LIMITTERS
            if (receivedChar == '2') {Timer1.start(4000);}
            if (receivedChar == '3') {Timer1.start(5000);}

            USDetection = 1;
            while (1) {
                if (receivedChar == '1') {
                    d1 = Sonar1.ping_cm(); delay(30);
                    if ((d1 < DistanceThreshold)) {delay(500);break;}
                }
                if (receivedChar == '2') {
                    d2 = Sonar2.ping_cm(); delay(30);
                    if ((d2 < DistanceThreshold)) {delay(300);break;}
                }
                if (receivedChar == '3') {
                    d3 = Sonar3.ping_cm(); delay(30);
                    if ((d3 < DistanceThreshold)) {break;}
                }
                if (Timer1.justFinished()) {
                    USDetection = 0;
                    break;
                }
            }
            digitalWrite(Conveyor_Pin, HIGH); 
  }


void ToggleLH(long delayings, int relayName) {      //toggle low to high
    digitalWrite(relayName, LOW); delay(delayings);
    digitalWrite(relayName, HIGH);
}

void ToggleHL(long delayings, int relayName) {      //toggle high to low
    digitalWrite(relayName, HIGH); delay(delayings);
    digitalWrite(relayName, LOW);
}

void RelayLOWwithLimit(int relayName, int MSName) {
    if (digitalRead(MSName) == 1){
        digitalWrite(relayName, LOW); delay(50);
        while(1) {if (digitalRead(MSName) == 0) {break;}}
        digitalWrite(relayName, HIGH);
    }
}

void LCDprint(int x, int y, String z) {
    lcd.setCursor(x,y); lcd.print(z);
}

void LCDClear() {
    LCDprint(0,0,"					");
    LCDprint(0,1,"					");
    LCDprint(0,2,"					");
    LCDprint(0,3,"					");
}
