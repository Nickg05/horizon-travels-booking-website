#Nickolas Greiner Student Id: 24018357

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
import mysql.connector
from mysql.connector import errorcode
from markupsafe import escape
from datetime import timedelta
import datetime  # Add this import for datetime.date and datetime.datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO  # Import BytesIO for in-memory file handling
from decimal import Decimal  # Import Decimal for precise arithmetic

# MYSQL CONFIG VARIABLES
hostname = "127.0.0.1"
username = "nickolas2greiner"
passwd = "Nickolas2greineR16+$++"
db = "nickolas2greiner"

# Function to get the database connection
def getConnection():    
    try:
        conn = mysql.connector.connect(
            host=hostname,                              
            user=username,
            password=passwd,
            db=db
        )  
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)
        return None  # Return None if there is an error

# Flask app setup
app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.permanent_session_lifetime = timedelta(days=1)

# The route for the homepage
@app.route('/')
def welcome():
    # Fetch unique departure and arrival locations along with their times from the 'journeys' table
    conn = getConnection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch departures and corresponding times
            cursor.execute("SELECT DISTINCT departure, departure_time FROM journeys")
            departures = cursor.fetchall()

            # Fetch arrivals and corresponding times
            cursor.execute("SELECT DISTINCT arrival, arrival_time FROM journeys")
            arrivals = cursor.fetchall()
        
            # Check if the user is logged in and pass the data to the template
            if 'logged_in' in session:
                return render_template('index.html', username=session['username'], departures=departures, arrivals=arrivals)
            else:
                return render_template('index.html', departures=departures, arrivals=arrivals)
        
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'error')
            return render_template('index.html')  # In case of error, just return the template
        
        finally:
            cursor.close()
            conn.close()

    else:
        flash('Database connection failed', 'error')
        return render_template('index.html')  # In case of connection failure, return the template


# The route for fetching arrivals based on selected departure
@app.route('/get_arrival')
def get_arrival():
    # Get the selected departure from the query parameters
    departure = request.args.get('departure')

    # Ensure the departure is provided
    if not departure:
        return jsonify({'error': 'Departure is required'}), 400

    # Fetch the corresponding arrivals from the 'journeys' table
    conn = getConnection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Query the database for all arrivals that match the selected departure
            cursor.execute("SELECT DISTINCT arrival, COALESCE(arrival_time, 'N/A') AS arrival_time FROM journeys WHERE departure = %s", (departure,))
            arrival = cursor.fetchall()
        
            # Return the arrival as a JSON response
            return jsonify({'arrival': arrival})

        except mysql.connector.Error as err:
            return jsonify({'error': str(err)}), 500

        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'error': 'Database connection failed'}), 500

# The route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']
        
        # Check the database for the user
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Check if the username and password match
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()  # Fetch one user
                
                # Ensure there are no unread results
                cursor.fetchall()  # Consume any remaining rows
                
                if user and user['password'] == password:  # Simple password check
                    # Set the session when login is successful
                    session['logged_in'] = True
                    session['username'] = user['username']  # Store the username
                    session['email'] = user['email']  # Store the email
                    session['user_id'] = user['userID']  # Store user ID in session for future reference
                    session['is_admin'] = user['is_admin'] == 1  # Check if the user is an admin (1 for admin, 0 for non-admin)
                    print(f"User logged in: {session['user_id']}, Admin: {session['is_admin']}")  # Debug print
                    return redirect(url_for('welcome'))  # Redirect to the homepage or a dashboard
                else:
                    flash('Invalid username or password', 'error')  # Flash an error message
                
            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'error')
            finally:
                cursor.close()  # Always close the cursor
                conn.close()  # Always close the connection
        else:
            flash('Database connection failed', 'error')
    
    return render_template('login.html')


# The route for logout
@app.route('/logout')
@app.route('/logout')
def logout():
    # Remove the session data
    session.clear()  # Clears all session data (a cleaner approach than using session.pop())
    
    # Optionally, you can log a message for debugging purposes
    print("User logged out")  # This can be removed after debugging
    
    # Redirect to the homepage (or 'welcome' page) after logout
    return redirect(url_for('welcome'))  # Make sure 'welcome' is the correct endpoint


# The route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        userID = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Create the connection
        conn = getConnection()
        
        if conn:
            cursor = conn.cursor()
            try:
                # Insert user data into the users table
                cursor.execute("""INSERT INTO users (username, password, email) 
                                  VALUES (%s, %s, %s)""", (userID, password, email))
                
                # Commit the transaction
                conn.commit()
                
                # Optionally, redirect to login or some success page
                return redirect(url_for('login'))
                
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                return "Error while registering user."
            finally:
                cursor.close()
                conn.close()
        
        else:
            return "Database connection failed."
    
    return render_template('register.html')

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'logged_in' in session:
        user_id = session.get('user_id')
        new_password = request.form.get('password')

        if not new_password:
            flash("Password is required.", "error")
            return redirect(url_for('user_profile'))

        conn = getConnection()
        if conn:
            cursor = conn.cursor()
            try:
                # Update only the user's password in the database
                cursor.execute("""
                    UPDATE users 
                    SET password = %s 
                    WHERE userID = %s
                """, (new_password, user_id))
                conn.commit()

                flash("Password updated successfully.", "success")
            except mysql.connector.Error as err:
                flash(f"Error updating password: {err}", "error")
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection failed.", "error")
    else:
        flash("You must be logged in to update your password.", "warning")

    return redirect(url_for('user_profile'))

@app.route('/user')
def user_profile():
    if 'logged_in' in session:
        username = session.get('username', 'Guest')
        email = session.get('email', 'N/A')  # Fetch email from session or database if needed
        password = "******"  # Masked password; fetch from database if required
        return render_template('user.html', username=username, email=email, password=password)
    else:
        flash("You must be logged in to view your profile.", "warning")
        return redirect(url_for('login'))


@app.route('/bookings')
def bookings():
    if 'logged_in' in session:
        # Get the logged-in user's ID
        user_id = session.get('user_id')
        print(f"Debug: Logged-in user ID: {user_id}")  # Debug print

        if not user_id:
            flash("User ID not found in session.", "error")
            return redirect(url_for('login'))

        # Fetch bookings for the logged-in user
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(""" 
                    SELECT b.bookingID, b.journeyID, b.seat_type, b.num_seats, b.travel_date, 
                           b.departure, b.arrival, b.departure_time, b.arrival_time, j.fare
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    WHERE b.userID = %s
                """, (user_id,))
                bookings = cursor.fetchall()

                # Convert timedelta and other non-serializable objects to strings
                for booking in bookings:
                    for key, value in booking.items():
                        if isinstance(value, timedelta):
                            booking[key] = str(value)
                        elif isinstance(value, (datetime.date, datetime.datetime)):
                            booking[key] = value.isoformat()

                    # Adjust the fare based on the seat type and round to the nearest pound
                    if booking['seat_type'] == 'Business':
                        booking['fare'] = round(booking['fare'] * Decimal(2))  # Double the fare for Business and round
                    elif booking['seat_type'] == 'Economy':
                        booking['fare'] = round(booking['fare'] * Decimal(1.2))  # Add 20% for Economy and round

                print(f"Debug: Bookings fetched: {bookings}")  # Debug print

                if not bookings:
                    flash("No bookings found for the user.", "info")
                return render_template('bookings.html', bookings=bookings)
            except mysql.connector.Error as err:
                flash(f"Error fetching bookings: {err}", 'error')
                return redirect(url_for('welcome'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection failed', 'error')
            return redirect(url_for('welcome'))
    else:
        flash("Please log in to access your bookings.", "warning")
        return redirect(url_for('login'))


@app.route('/add_booking', methods=['POST'])
def add_booking():
    booking_details = request.get_json()

    # Ensure the necessary fields are provided
    required_fields = ['departure', 'arrival', 'departureTime', 'arrivalTime', 'travelDate', 'seatType', 'numSeats', 'paymentDetails']

    for field in required_fields:
        if field not in booking_details or not booking_details[field]:
            print(f"Debug: Missing or invalid field: {field}")  # Debug log
            return jsonify({'error': f'Missing or invalid field: {field}'}), 400

    # Fetch the user_id from session (assuming user is logged in)
    user_id = session.get('user_id')
    if not user_id:
        print("Debug: User not logged in")  # Debug log
        return jsonify({'error': 'User not logged in'}), 403

    # Extract payment details
    payment_details = booking_details['paymentDetails']
    card_number = payment_details.get('cardNumber')
    expiry_date = payment_details.get('expiryDate') + "-01"  # Append "-01" to make it a valid DATE format
    cardholder_name = payment_details.get('cardholderName')
    cvc = payment_details.get('cvv')

    # Insert the booking and payment details into the database
    conn = getConnection()
    if conn:
        cursor = conn.cursor()
        try:
            # Insert the booking into the bookings table
            cursor.execute("""
                INSERT INTO bookings (userID, seat_type, num_seats, departure, arrival, departure_time, arrival_time, travel_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                booking_details['seatType'],
                booking_details['numSeats'],
                booking_details['departure'],
                booking_details['arrival'],
                booking_details['departureTime'],
                booking_details['arrivalTime'],
                booking_details['travelDate']
            ))

            # Insert the payment details into the paycardinfo table
            cursor.execute("""
                INSERT INTO paycardinfo (CardNo, Exp, userID, cvc, cardholdername)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                card_number,
                expiry_date,  # Use the converted expiry date
                user_id,
                cvc,
                cardholder_name
            ))

            conn.commit()
            print("Debug: Booking and payment details successfully added")  # Debug log
            return jsonify({'success': True}), 200
        except mysql.connector.Error as err:
            print(f"Debug: Database error: {err}")  # Debug log
            return jsonify({'error': str(err)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        print("Debug: Database connection failed")  # Debug log
        return jsonify({'error': 'Database connection failed'}), 500


@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    if 'logged_in' in session:
        booking_id = request.form.get('bookingID')

        if not booking_id:
            flash("Booking ID is required to cancel a booking.", "error")
            return redirect(url_for('bookings'))

        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Fetch the booking details
                cursor.execute("""
                    SELECT travel_date, num_seats, seat_type, j.fare
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    WHERE b.bookingID = %s AND b.userID = %s
                """, (booking_id, session['user_id']))
                booking = cursor.fetchone()

                # Consume any remaining results to avoid "Unread result found"
                cursor.fetchall()

                if not booking:
                    flash("Booking not found or access denied.", "error")
                    return redirect(url_for('bookings'))

                # Use the travel_date directly as it is already a datetime.date object
                travel_date = booking['travel_date']
                today = datetime.date.today()
                days_until_travel = (travel_date - today).days
                total_fare = booking['fare'] * booking['num_seats']

                if days_until_travel > 60:
                    refund_amount = total_fare  # Full refund
                    message = f"Your booking has been canceled. You will receive a full refund of £{refund_amount:.2f}."
                elif 30 < days_until_travel <= 60:
                    refund_amount = total_fare * 0.6  # 40% cancellation charge
                    message = f"Your booking has been canceled. A 40% cancellation charge applies. You will receive a refund of £{refund_amount:.2f}."
                elif days_until_travel <= 30:
                    refund_amount = 0  # No refund
                    message = f"Your booking has been canceled. No refund is available as the cancellation is within 30 days of the travel date."

                # Delete the booking from the database
                cursor.execute("DELETE FROM bookings WHERE bookingID = %s AND userID = %s", (booking_id, session['user_id']))
                conn.commit()

                flash(message, "success")
            except mysql.connector.Error as err:
                flash(f"Error canceling booking: {err}", "error")
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection failed.", "error")
    else:
        flash("You must be logged in to cancel a booking.", "warning")

    return redirect(url_for('bookings'))


@app.route('/admin/bookings')
def admin_bookings():
    if 'logged_in' in session and session.get('is_admin'):
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Fetch all bookings
                cursor.execute("""
                    SELECT bookingID, journeyID, seat_type, num_seats, travel_date, 
                           departure, arrival, departure_time, arrival_time, userID
                    FROM bookings
                """)
                bookings = cursor.fetchall()

                # Fetch all users
                cursor.execute("SELECT userID, username, email FROM users")
                users = cursor.fetchall()

                # Calculate monthly sales
                cursor.execute("""
                    SELECT SUM(j.fare * b.num_seats) AS monthly_sales
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    WHERE MONTH(b.travel_date) = MONTH(CURRENT_DATE())
                """)
                monthly_sales = cursor.fetchone()['monthly_sales'] or 0

                # Fetch top customers
                cursor.execute("""
                    SELECT u.username, SUM(j.fare * b.num_seats) AS total_spent
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    JOIN users u ON b.userID = u.userID
                    GROUP BY u.username
                    ORDER BY total_spent DESC
                    LIMIT 5
                """)
                top_customers = cursor.fetchall()

                # Fetch profitable routes
                cursor.execute("""
                    SELECT b.departure, b.arrival, SUM(j.fare * b.num_seats) AS total_revenue
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    GROUP BY b.departure, b.arrival
                    HAVING total_revenue > 0
                    ORDER BY total_revenue DESC
                """)
                profitable_routes = cursor.fetchall()

                # Fetch loss-making routes
                cursor.execute("""
                    SELECT b.departure, b.arrival, SUM(j.fare * b.num_seats) AS total_revenue
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    GROUP BY b.departure, b.arrival
                    HAVING total_revenue <= 0
                    ORDER BY total_revenue ASC
                """)
                loss_making_routes = cursor.fetchall()

                return render_template(
                    'admin_bookings.html',
                    bookings=bookings,
                    users=users,
                    monthly_sales=monthly_sales,
                    top_customers=top_customers,
                    profitable_routes=profitable_routes,
                    loss_making_routes=loss_making_routes
                )
            except mysql.connector.Error as err:
                flash(f"Error fetching data: {err}", 'error')
                return redirect(url_for('welcome'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection failed', 'error')
            return redirect(url_for('welcome'))
    else:
        flash("Access denied. Admins only.", "error")
        return redirect(url_for('login'))

@app.route('/admin/change_password', methods=['POST'])
def admin_change_password():
    if 'logged_in' in session and session.get('is_admin'):
        user_id = request.form.get('user_id')
        new_password = request.form.get('new_password')

        if not user_id or not new_password:
            flash("User ID and new password are required.", "error")
            return redirect(url_for('admin_bookings'))

        conn = getConnection()
        if conn:
            cursor = conn.cursor()
            try:
                # Update the user's password
                cursor.execute("UPDATE users SET password = %s WHERE userID = %s", (new_password, user_id))
                conn.commit()
                flash("Password updated successfully.", "success")
            except mysql.connector.Error as err:
                flash(f"Error updating password: {err}", "error")
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection failed.", "error")
    else:
        flash("Access denied. Admins only.", "error")

    return redirect(url_for('admin_bookings'))

@app.route('/admin/cancel_booking', methods=['POST'])
def admin_cancel_booking():
    if 'logged_in' in session and session.get('is_admin'):
        booking_id = request.form.get('bookingID')

        if not booking_id:
            flash("Booking ID is required to cancel a booking.", "error")
            return redirect(url_for('admin_bookings'))

        conn = getConnection()
        if conn:
            cursor = conn.cursor()
            try:
                # Delete the booking from the database
                cursor.execute("DELETE FROM bookings WHERE bookingID = %s", (booking_id,))
                conn.commit()

                flash("Booking canceled successfully.", "success")
            except mysql.connector.Error as err:
                flash(f"Error canceling booking: {err}", "error")
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection failed.", "error")
    else:
        flash("Access denied. Admins only.", "error")

    return redirect(url_for('admin_bookings'))

@app.route('/get_fare', methods=['GET'])
def get_fare():
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')

    if not departure or not arrival:
        return jsonify({'error': 'Departure and arrival are required'}), 400

    conn = getConnection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Query the fare for the selected journey
            cursor.execute("""
                SELECT fare 
                FROM journeys 
                WHERE departure = %s AND arrival = %s
            """, (departure, arrival))
            result = cursor.fetchone()  # Fetch one result

            # Ensure there are no unread results
            cursor.fetchall()  # Consume any remaining rows

            if result:
                return jsonify({'fare': result['fare']})
            else:
                return jsonify({'error': 'Journey not found'}), 404
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)}), 500
        finally:
            cursor.close()  # Close the cursor after all results are consumed
            conn.close()  # Close the connection
    else:
        return jsonify({'error': 'Database connection failed'}), 500

@app.route('/download_ticket/<int:booking_id>', methods=['GET'])
def download_ticket(booking_id):
    if 'logged_in' in session:
        user_id = session.get('user_id')

        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                # Fetch the booking details for the given booking ID and user ID
                cursor.execute("""
                    SELECT b.bookingID, b.journeyID, b.seat_type, b.num_seats, b.travel_date, 
                           b.departure, b.arrival, b.departure_time, b.arrival_time, j.fare
                    FROM bookings b
                    JOIN journeys j ON b.departure = j.departure AND b.arrival = j.arrival
                    WHERE b.bookingID = %s AND b.userID = %s
                """, (booking_id, user_id))
                booking = cursor.fetchone()

                if not booking:
                    flash("Booking not found or access denied.", "error")
                    return redirect(url_for('bookings'))

                # Generate the PDF in memory
                pdf_buffer = BytesIO()
                pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
                pdf.setTitle(f"Ticket #{booking_id}")

                # Add ticket details to the PDF
                pdf.drawString(100, 750, "Horizon Travels - Booking Ticket")
                pdf.drawString(100, 730, f"Booking ID: {booking['bookingID']}")
                pdf.drawString(100, 710, f"Journey ID: {booking['journeyID']}")
                pdf.drawString(100, 690, f"Departure: {booking['departure']} at {booking['departure_time']}")
                pdf.drawString(100, 670, f"Arrival: {booking['arrival']} at {booking['arrival_time']}")
                pdf.drawString(100, 650, f"Travel Date: {booking['travel_date']}")
                pdf.drawString(100, 630, f"Seat Type: {booking['seat_type']}")
                pdf.drawString(100, 610, f"Number of Seats: {booking['num_seats']}")
                pdf.drawString(100, 590, f"Total Fare: £{booking['fare'] * booking['num_seats']}")

                pdf.save()
                pdf_buffer.seek(0)  # Move the buffer's cursor to the beginning

                # Create a Flask response with the PDF
                response = make_response(pdf_buffer.getvalue())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename=ticket_{booking_id}.pdf'

                return response

            except mysql.connector.Error as err:
                flash(f"Error generating ticket: {err}", "error")
                return redirect(url_for('bookings'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection failed.", "error")
            return redirect(url_for('bookings'))
    else:
        flash("You must be logged in to download tickets.", "warning")
        return redirect(url_for('login'))

@app.route('/update_booking/<int:booking_id>', methods=['GET', 'POST'])
def update_booking(booking_id):
    if 'logged_in' in session:
        user_id = session.get('user_id')

        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                if request.method == 'POST':
                    # Handle the form submission to update the booking
                    travel_date = request.form['travel_date']
                    num_seats = request.form['num_seats']
                    seat_type = request.form['seat_type']

                    # Update the booking in the database
                    cursor.execute("""
                        UPDATE bookings
                        SET travel_date = %s, num_seats = %s, seat_type = %s
                        WHERE bookingID = %s AND userID = %s
                    """, (travel_date, num_seats, seat_type, booking_id, user_id))
                    conn.commit()

                    flash("Booking updated successfully.", "success")
                    return redirect(url_for('bookings'))

                # Fetch the booking details for the given booking ID
                cursor.execute("""
                    SELECT bookingID, travel_date, num_seats, seat_type
                    FROM bookings
                    WHERE bookingID = %s AND userID = %s
                """, (booking_id, user_id))
                booking = cursor.fetchone()

                if not booking:
                    flash("Booking not found or access denied.", "error")
                    return redirect(url_for('bookings'))

                return render_template('update_booking.html', booking=booking)

            except mysql.connector.Error as err:
                flash(f"Error updating booking: {err}", "error")
                return redirect(url_for('bookings'))
            finally:
                cursor.close()
                conn.close()
        else:
            flash("Database connection failed.", "error")
            return redirect(url_for('bookings'))
    else:
        flash("You must be logged in to update a booking.", "warning")
        return redirect(url_for('login'))

@app.route('/test-db')
def test_db_connection():
    # Get the database connection
    conn = getConnection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")  # Simple query to test connection
            result = cursor.fetchone()  # Fetch one result (should be `1` if the connection works)
            
            if result:
                return "Database connection is successful!"  # Success message
            else:
                return "Error: Unable to fetch data from the database."
        except mysql.connector.Error as err:
            return f"Database connection failed: {err}"  # Display error if connection fails
        finally:
            cursor.close()
            conn.close()
    else:
        return "Failed to connect to the database."

if __name__ == '__main__': 
    for i in range(10000, 18000):
        try:
            app.run(debug=True, port=i)
            break
        except OSError as e:
            print(f"Port {i} not available")


