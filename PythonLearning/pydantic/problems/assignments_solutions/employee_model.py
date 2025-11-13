from pydantic import BaseModel,Field
from typing import Dict, List, Optional

# Create a model with Fields: 
# -- id : int
# -- name : str (min 3 characters  )
# -- department : Optional str (default 'General')   
# -- salary : float (greater than 01000)
# ... means required field 
# Use Field to add constraints and descriptions, examples
# examples can be a single example or a list of examples

class Employee(BaseModel):
    id:int
    name: str=Field(...,
                    min_length=3,
                    max_length=10,
                    description="Employee Name must be between 3 and 10 characters",
                    examples="Ana"
                    )
    depaartment: Optional[str] = 'General'
    salary: float = Field(...,
                            ge=1000,
                            description="Salary must be greater than 1000",
                            examples=[1500.50, 2000.75]
                            )

