from fastapi import FastAPI,Path,HTTPException,Query
import json

app= FastAPI()

def loadData():
    with open("patients.json", "r") as f:
        return json.load(f)

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