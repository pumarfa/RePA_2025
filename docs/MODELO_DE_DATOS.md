# Modelo de datos RePA 2025

## Modelo de datos sugerido

---

### **1. Diagrama de Datos**  
```mermaid
graph TD

classDiagram
    class User {
        <<Abstract>>
        +uuid id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
        +String email = Column(String, unique=True, index=True, nullable=False)
        +String hashed_password = Column(String, nullable=False)
        +Boolean is_active = Column(Boolean, default=True)
        +DateTime created_at = Column(DateTime, default=datetime.utcnow)
        +DateTime last_login = Column(DateTime, default=None, nullable=True)
    }
    
    class Role {
        <<Abstract>>
        +int id = Column(Integer, primary_key=True, index=True)
        +String rol = Column(String, unique=True, index=True, nullable=False)
    }

    class UserRole {
        +int id = Column(Integer, primary_key=True, index=True)
        +String user_id = Column(String, ForeignKey("users.id"))
        +id role_id = Column(Integer, ForeignKey("roles.id"))
    }


    User "1" -->  User : assignedTo
    User <|-- UserRole : Inheritance
    User "0" --> "many" Role
    Role "0" --> UserRole : User_id
    
    style User fill:#bfb,stroke:#6f6,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    style UserRole fill:#9ff,stroke:#369,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    style Role fill:#ffb,stroke:#663,stroke-width:2px,color:#000,stroke-dasharray: 5 5

```

---

## Diccionario de Datos

