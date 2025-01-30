# **Smart Trash Bin**  
An AI-powered waste classification and sorting system  

## **Authors**  
- Mihai Buliga – University of Twente  
- Illia Solodkyi – University of Twente  
- Mohamed Soliman – University of Twente  
- Pavlo Hrechko – University of Twente  
- Karan Matilal – University of Twente  

## **Overview**  
The **Smart Trash Bin** is an automated waste sorting system that uses **artificial intelligence (AI)** to identify and classify waste into categories such as **organic, paper, plastic, and metal**. By integrating a **computer vision model**, a **motorized bin mechanism**, and a **wireless communication system**, this project aims to improve **waste sorting efficiency** while reducing human effort.  

## **Key Features**  
- **AI-Powered Classification**: Uses a trained **neural network** to classify waste.  
- **Automated Sorting**: A **servo-controlled chute and rotating bins** sort the waste into appropriate categories.  
- **Bluetooth Communication**: Coordinates between multiple Raspberry Pis for classification and sorting.  
- **User-Friendly Design**: Simple button press initiates the sorting process.  

## **System Workflow**  
1. User places waste on the scanning platform.  
2. AI model classifies the waste from a captured image.  
3. Classification result is sent to the **control unit** via Bluetooth.  
4. The **motorized bin** rotates to the correct position.  
5. The **chute mechanism** releases the waste into the appropriate bin.  

## **Hardware Components**  
- **Raspberry Pi** for processing and communication  
- **Camera module** for image capture  
- **Stepper motors** for rotating bins  
- **Servo motors** for the chute mechanism  
- **Edge Impulse AI model** for waste classification  

## **Software and AI Model**  
- Uses **computer vision (CNN model)** for image classification  
- Implemented in **Python** with **OpenAI API** for AI-based classification  
- **Bluetooth communication** between Raspberry Pis for system coordination  

## **Results**  
- **89.6% classification accuracy** across waste types  
- Sorting process completed in an **average of 15 seconds** per item  

## **Future Improvements**  
- **Enhancing classification accuracy**, especially for organic waste  
- **Reducing processing time** by optimizing bin rotation  
- **Expanding material classification** for better recycling accuracy  

## **Setup Instructions**  
### **1. Install Dependencies**  
```bash
pip install openai edge_impulse_linux opencv-python numpy gpiozero bluetooth
```

### **2. Run the System**  
```bash
python button.py
```

## **License**  
This project is licensed under **ACM rights** and is intended for academic and research purposes.  
