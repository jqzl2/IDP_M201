int tsopPin = 2;
int qsdPin1 = A2;
int qsdPin2 = A3;

int tsop = 0;  // variable to store the value read
int qsd1 = 0;
int qsd2 = 0;

/*
unsigned long cycle_a;
unsigned long cycle_a1;
unsigned long cycle_b;
unsigned long cycle_b1;
unsigned long cycle_b2;
*/


void setup() {
  Serial.begin(115200);           //  takes new readings every ... µs (baud rate)
}

int dummyMode() {
  qsd1 = analogRead(qsdPin1);
  qsd2 = analogRead(qsdPin2);

  int Mode = 0;
  
  //Serial.println((String)"tsop:" + tsop);          // debug value
  //Serial.println((String)"qsd1:" + qsd1);
  //Serial.println((String)"qsd2:" + qsd2);


///*
  // dummy signal detected (1 = 0.049mV)
  if (qsd1 > 200 || qsd2 > 200){
        
        // 38kHz detected (1st cycle)
        tsop = digitalRead(tsopPin);
        //cycle_a = micros();     //time begins
        
        if (tsop == 0){

          // 38kHz detected (2nd cycle)
          delay(6);    //wait for 6ms to take cycle2 reading
          tsop = digitalRead(tsopPin);
          
          //cycle_a1 = micros();    //time ends
          //Serial.print("cycle time: ");
          //Serial.println(cycle_a1-cycle_a);
          
          if (tsop == 0){
            //Serial.println((String)"Mode 1 - 11");     // Mode = 1
            Mode = 1;
            // set R and G LED on
          // 38kHz not detected (2nd cycle)
            }
          else {
            //Serial.println((String)"Mode 3 - 12");     // Mode = 3
            Mode = 3;
            // set G LED on
          }
          }
        


        // 38kHz not detected (1st cycle) - examine if due to phase difference
        else if (tsop == 1){
          int t = 0;    // t starts when intensity detected
          do{
            tsop = digitalRead(tsopPin);
            t++;  // check if tsop falls
          } while (t <= 7 && tsop == 1);
          //cycle_b = micros();
            
          // phase difference! 38kHz detected (1st cycle)
          if (tsop == 0){
             // 38kHz detected (2nd cycle)
            delay(6);
            tsop = digitalRead(tsopPin);
            //cycle_b1 = micros();     //time ends
            //Serial.print("cycle time: ");
            //Serial.println(cycle_b1-cycle_b);
            
            
            if (tsop == 0){
              //Serial.println((String)"Mode 1 - 21");   // Mode = 1
              Mode = 1;
              // set R and G LED on
            }
            // 38kHz not detected (2nd cycle)
            else if (tsop == 1){
              //Serial.println((String)"Mode 3 - 22");   // Mode = 3
              Mode = 3;
              // set G LED on
              }
            }
          
          // 38kHz not detected (1st cycle) - not due to phase difference
          else {
            delay(6);    // wait for 5ms and check for a duration of 1ms
            int i = 0;    // t starts when intensity detected
            do{
              tsop = digitalRead(tsopPin);
              i++;  // check if tsop falls
            } while (i <= 10 && tsop == 1);
            //cycle_b2 = micros();
            //Serial.print("cycle time: ");
            //Serial.println(cycle_b2-cycle_b);
            
            // 38kHz undetected (2nd)
            if (tsop == 1){
              //Serial.println((String)"Mode 2 - 31");   // Mode = 2
              Mode = 2;
              // set R LED on
            }
            // 38kHz detected (2nd)
            else {
              //Serial.println((String)"Mode 3 - 32");   // Mode = 3
              Mode = 3;
              // set G LED on
            }
          }
        }
 }
 return Mode;

}

void loop(){

  int mode_sum = 0;
  int count = 100;
  int mode = 0;
  while(count != 0){
    mode = dummyMode();
    if (mode != 0){
      mode_sum += mode - 2;
      count -=1;
    }
    
  }
  //Serial.println(mode_sum);

  // adjust the threshold value to change accuracy
  if (mode_sum > 50){
    //Serial.println("Mode is");
    Serial.println(3);
  }
  else if (mode_sum < -50){
    //Serial.println("Mode is");
    Serial.println(1);
  }
  else{
    //Serial.println("Mode is");
    Serial.println(2);
  }

  delay(1);
}
