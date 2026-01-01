# Parking Lot Management App

This repository contains a **Flask-based Parking Lot Management System** that enables users to book parking spots, track active and past reservations, and allows administrators to manage parking lots, spots, and bookings. The application uses a **SQLite database** and provides role-based functionality for **users and admins**.

---

## Project Overview

This project simulates a real-world parking management workflow where:
- Users can register, log in, book parking spots, and view bills and history
- Admins can create and manage parking lots, monitor usage, and view system-wide analytics
- Parking availability updates dynamically based on bookings and completions

The system is designed with **database integrity, transactional consistency, and practical validation logic** in mind.

---

## Core Features

### User Features
- User registration and authentication
- Vehicle registration during booking
- Browse available parking lots
- Book parking spots in real time
- Complete parking sessions
- View bills and detailed booking history

### Admin Features
- Admin login
- Create, update, and delete parking lots
- Dynamically add or remove parking spots
- Prevent deletion of occupied lots
- View all users, vehicles, bookings, and parking statistics
- Global parking usage dashboard

---

## System Architecture

### Backend
- **Flask** – Web framework and routing
- **WTForms** – Form handling and validation
- **SQLite3** – Relational database
- **Jinja2** – Template rendering

### Database Design
The system uses a normalized relational schema with the following tables:

- `User`
- `Vehicles`
- `ParkingLots`
- `ParkingSpots`
- `Bookings`

Foreign key constraints ensure referential integrity between users, vehicles, spots, and lots.

