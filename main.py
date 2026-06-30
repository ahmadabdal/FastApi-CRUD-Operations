from fastapi import FastAPI,Path,HTTPException,Query
import json
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional 

app= FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The ID of the patient")]
    name: Annotated[str, Field(..., description="The name of the patient")]
    city: Annotated[str, Field(..., description="The city of the patient")]
    age: Annotated[int, Field(..., description="The age of the patient")]
    gender: Annotated[Literal ['male', 'female', 'other'], Field(..., description="The gender of the patient")]
    height: Annotated[float, Field(...,gt=0, description="The height of the patient")]
    weight: Annotated[float, Field(...,gt=0, description="The weight of the patient")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)

class PatientUpdate(BaseModel):
    name:Annotated[Optional[str], Field(None, description="The name of the patient")]
    city:Annotated[Optional[str], Field(None, description="The city of the patient")]
    age:Annotated[Optional[int], Field(None, description="The age of the patient")]
    gender:Annotated[Optional[Literal ['male', 'female', 'other']], Field(None, description="The gender of the patient")]
    height:Annotated[Optional[float], Field(None,gt=0, description="The height of the patient")]
    weight:Annotated[Optional[float], Field(None,gt=0, description="The weight of the patient")]
def loadData():
    with open("patients.json", "r") as f:
        return json.load(f)
    
def saveData(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)  

@app.get("/")
def hello():
    return {"message": "Welcome to patient management system"}

@app.get("/patients")
def get_patients():
    data=loadData()
    return data

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str=Path(..., description="The ID of the patient to retrieve",example="P001"   )):
    data = loadData()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort/patients")
def sort_patients(sort_by : str= Query(...,description="Sort on basis of Height,weight and BMI"),order: str=Query('asc', description='sort in asc or des order')):
  valid_fields = ['height', 'weight', 'bmi']
  if sort_by not in valid_fields:
    raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}")
  if order not in ['asc', 'desc']:
    raise HTTPException(status_code=400, detail="Invalid sort order. Valid orders are: 'asc' or 'desc'")
  data = loadData()
  sort_order = True if order == 'desc' else False
  sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=sort_order)
  return sorted_data

@app.post("/create/patient")
def create_patient(patient: Patient):
   data = loadData()
   # Check if the patient ID already exists in the data
   if patient.id in data:
       raise HTTPException(status_code=400, detail="Patient with this ID already exists")
   #new patient added to the data dictionary with computed fields included
   data[patient.id] =patient.model_dump(exclude=['id'])  # Ensure computed fields are included

   #save the updated data back to the JSON file
   saveData(data)
   return JSONResponse(content={"message": "Patient created successfully"}, status_code=201)

@app.put("/update/patient/{patient_id}")
def update_patient(patient_id: str, patient: PatientUpdate):
    data = loadData()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    existing_patient = data[patient_id]
    updated_patient =patient.model_dump(exclude_unset=True)

    for key, value in updated_patient.items():
        existing_patient[key] = value

    existing_patient['id'] = patient_id  # Ensure the ID remains unchanged
    patient_obj = Patient(**existing_patient)  # Create a Patient object to compute BMI
    existing_patient =patient_obj.model_dump(exclude=['id'])  # Update the existing patient data with computed fields
    data[patient_id] = existing_patient    

    saveData(data)
    return JSONResponse(content={"message": "Patient updated successfully"}, status_code=200)
    
  
