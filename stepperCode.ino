// Define pin connections & motor's steps per revolution
const int dirPin = 2;
const int stepPin = 3;
const int stepsPerRevolution = 3200;

// Track current position (0: Up, 1: Right, 2: Down, 3: Left)
int currentPosition = 0;

void setup()
{
  // Initialize serial communication
  Serial.begin(9600);

  // Declare pins as Outputs
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

  Serial.println("Enter a number (0: Up, 1: Right, 2: Down, 3: Left):");
}

void loop()
{
  // Check if data is available on the serial monitor
  if (Serial.available() > 0)
  {
    // Read the input as a string and trim whitespace
    String inputString = Serial.readStringUntil('\n');
    inputString.trim();

    // Convert the string to an integer
    int input = inputString.toInt();
    Serial.println("recieved: " + input);
   

    if (input >= 0 && input <= 3)
    {
      // Calculate the target position based on input
      int targetPosition = input;

      // Calculate the steps to move (positive for clockwise, negative for counter-clockwise)
      int stepsToMove = calculateSteps(currentPosition, targetPosition);

      // Move the motor
      moveMotor(stepsToMove > 0, abs(stepsToMove));

      // Update the current position
      currentPosition = targetPosition;
    }
    else
    {
      Serial.println("Invalid input! Enter a number between 0 and 3.");
    }
  }
}

int calculateSteps(int current, int target)
{
  // Calculate the difference in positions
  int stepDifference = target - current;

  // Normalize to the shortest path (clockwise or counter-clockwise)
  if (stepDifference > 2) stepDifference -= 4;
  if (stepDifference < -2) stepDifference += 4;

  // Convert position difference to steps
  return stepDifference * (stepsPerRevolution / 4); // 90 degrees per direction
}

void moveMotor(bool clockwise, int steps)
{
  // Set motor direction
  digitalWrite(dirPin, clockwise ? HIGH : LOW);

  // Spin motor for the given steps
  for (int x = 0; x < steps; x++)
  {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(3000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(3000);
  }
  Serial.println(1); 
}
