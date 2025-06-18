from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

client = MongoClient("mongodb+srv://shivamediboena:22BCB7192@event.ucm7vfc.mongodb.net/")
db = client["Event"]
events = db["events"]
registrations = db["registrations"]

@app.route('/')
def home():
    all_events = list(events.find())
    return render_template("index.html", events=all_events)

@app.route('/event/new', methods=["GET", "POST"])
def new_event():
    if request.method == "POST":
        event = {
            "name": request.form["name"],
            "date": request.form["date"],
            "location": request.form["location"],
            "description": request.form["description"]
        }
        events.insert_one(event)
        flash("Event created successfully!", "success")
        return redirect(url_for('home'))
    return render_template("new_event.html")

@app.route('/event/<event_id>/edit', methods=["GET", "POST"])
def edit_event(event_id):
    event = events.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for('home'))
    if request.method == "POST":
        updated_event = {
            "name": request.form["name"],
            "date": request.form["date"],
            "location": request.form["location"],
            "description": request.form["description"]
        }
        events.update_one({"_id": ObjectId(event_id)}, {"$set": updated_event})
        flash("Event updated successfully!", "success")
        return redirect(url_for('home'))
    return render_template("edit_event.html", event=event)

@app.route('/event/<event_id>/delete')
def delete_event(event_id):
    events.delete_one({"_id": ObjectId(event_id)})
    registrations.delete_many({"event_id": event_id})
    flash("Event and its registrations deleted.", "danger")
    return redirect(url_for('home'))

@app.route('/event/<event_id>/register', methods=["GET", "POST"])
def register(event_id):
    event = events.find_one({"_id": ObjectId(event_id)})
    if not event:
        flash("Event not found.", "danger")
        return redirect(url_for('home'))
    if request.method == "POST":
        registration = {
            "event_id": event_id,
            "name": request.form["name"],
            "email": request.form["email"],
            "phone": request.form["phone"]
        }
        registrations.insert_one(registration)
        flash("Registration successful!", "success")
        return redirect(url_for('view_attendees', event_id=event_id))
    return render_template("register.html", event=event)

@app.route('/event/<event_id>/attendees')
def view_attendees(event_id):
    event = events.find_one({"_id": ObjectId(event_id)})
    attendees_list = list(registrations.find({"event_id": event_id}))
    return render_template("attendees.html", event=event, attendees=attendees_list)

if __name__ == '__main__':
    app.run(debug=True)
