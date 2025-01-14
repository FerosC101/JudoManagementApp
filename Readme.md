

# North Sussex Judo Management System

## Overview
The **North Sussex Judo Management System** is a robust platform designed to streamline operations for judo training facilities. It supports efficient athlete management, training coordination, competition tracking, and payment handling, enhancing the overall experience for administrators, athletes, and guests.

---

## Features
1. **Athlete Management**:
   - Register and manage athlete profiles.
   - Categorize athletes by weight and age for training and competitions.

2. **Training Plan Management**:
   - Add and delete training plans.
   - Define plans by sessions per week, fee structures, and categories.
   - Monitor athlete progress in enrolled training plans.

3. **Competition Management**:
   - Register athletes for competitions based on weight categories.
   - Manage competition details, including location, date, and entry fees.

4. **Payment Processing**:
   - Record and view payment history for training plans and competitions.
   - Support for multiple payment methods (e.g., cash, card).

5. **Admin Dashboard**:
   - Comprehensive tools to manage athletes, training plans, competitions, and payments.
   - Role-based access control for secure data management.

6. **User Authentication and Security**:
   - Role-based access (admin, athlete, guest).
   - Secure login with JWT authentication.
   - OWASP-compliant practices, including multi-factor authentication.

7. **Responsive Design**:
   - Accessible on desktop, tablet, and mobile devices.
   - Material Design principles for intuitive navigation.

---

## Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5.0)
- **Database**: PostgreSQL
- **Authentication**: JSON Web Tokens (JWT)
- **Architecture**: MVC (Model-View-Controller)

---

## Database Schema
### Tables
1. **Athletes**: Manage athlete details like name, age, and weight category.
2. **Training Plans**: Store training plan details, including fees and session frequency.
3. **Competitions**: Track competition information and athlete participation.
4. **Payments**: Record payments with methods, amounts, and plan types.
5. **Athlete Training**: Link athletes with their training plans.
6. **Athlete Competitions**: Register athletes for competitions.
7. **Users**: Manage user roles and account information.

### Highlights
- Fully normalized schema (up to 3NF).
- Supports foreign key constraints for data integrity.
- Indexing for optimized queries.

---

## Installation and Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/YourRepo/NorthSussexJudo.git
   cd NorthSussexJudo
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Create a PostgreSQL database.
   - Execute the provided database scripts in `db_scripts/`.

4. Run the application:
   ```bash
   flask run
   ```

5. Access the app:
   - Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Testing
Comprehensive test cases ensure the system's functionality and security:
1. **Authentication**: Secure login for admins, athletes, and guests.
2. **Dashboard Access**: Valid session redirection and data loading.
3. **Payment Processing**: Valid/invalid payment scenarios.
4. **Competition Registration**: Restrict based on training plan eligibility.
5. **Admin Controls**: Secure data management tools.

---

## Future Enhancements
- Mobile app integration for easier access.
- Real-time analytics for performance and progress tracking.
- Advanced reporting tools for training plans and competitions.
- Push notifications for competition updates and reminders.

---


