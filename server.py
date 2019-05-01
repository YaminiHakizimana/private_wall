from flask import Flask, render_template, request, redirect,flash, session
from flask_bcrypt import Bcrypt  
from  mysqlconnection import connectToMySQL         
import re
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key="krrkrkrkrttt"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

#registration PAGE

@app.route('/')
def registrationform():
    return render_template("index.html")


#Wall Page

@app.route('/wallpage')
def wall():
    mysql = connectToMySQL("private")
    if 'user_id' not in session:
        return redirect("/")
    else:
        query = 'SELECT * FROM users WHERE user_id = %(id)s;'
        data = {
            'id': session['user_id'],
        }
        users = mysql.query_db(query, data)
    
        mysql= connectToMySQL('private')
        query = 'SELECT * FROM users ORDER BY first_name;'
        recipients = mysql.query_db(query)
        mysql= connectToMySQL('private')
        
        query = 'SELECT users.user_id, users.first_name, messages.id, messages.recipient_id, messages.messages, messages.create_at FROM users JOIN messages ON users.user_id = messages.user_id WHERE recipient_id = %(rid)s;'
        data = {
        'rid': session['user_id']
        }
        display = mysql.query_db(query, data)
        total_messages= len(display)
        mysql= connectToMySQL('private')
        query= 'SELECT COUNT(*) FROM messages WHERE  user_id=%(id)s;'
        data= {
            'id': session['user_id'],
        }
        sent_messages= mysql.query_db(query, data)
        return render_template('welcomepage.html', all_users = users, recipients = recipients, display = display, total_messages=total_messages, sent_messages = sent_messages)
    

#registration Route

@app.route('/createUser', methods=['POST'])
def register():
      
      if len(request.form['fname']) < 2:
        is_valid = False
        flash("Your first Name should be more than just 2 characters")
        return redirect("/")
      if len(request.form['lname']) < 2:
        is_valid = False
        flash("Your last Name should be more than just 2 characters")
        return redirect("/")
      if not EMAIL_REGEX.match(request.form['email']):
        flash('Email is invalid!')
        return redirect("/")
      else: 
          mysql = connectToMySQL('private')
          query = 'SELECT * FROM users where email =%(em)s'
          data = {"em":request.form["email"]}
          result = mysql.query_db(query, data)
          if len(result) != 0:
              flash("the email is already taken please choose another")
      if len(request.form['pass']) < 8:
         flash('password must have more than 8 characters')
         return redirect("/")
      if request.form['pass'] != request.form['passcon']:
        flash('password must match')
     
        return redirect("/")
      else:
         pw_hash = bcrypt.generate_password_hash(request.form['pass'])
        
         mysql = connectToMySQL("private")
         query = "INSERT INTO users (first_name, last_name, email_address, password) VALUES (%(fn)s, %(lastn)s ,%(em)s, %(password_hash)s);"
         data = {
             "fn": request.form['fname'],
             "lastn": request.form['lname'],
             "em": request.form['email'],
             "password_hash":[pw_hash]
        }
         mysql.query_db(query, data)
      flash("your Email was successful created!!")
      return redirect("/")


#Log_in Page

@app.route("/log_in", methods=['POST'])
def log_in():
    mysql = connectToMySQL("private")
    query = "SELECT * FROM users WHERE email_address = %(em)s;"
    data = { "em" : request.form["email"] }
    result = mysql.query_db(query, data)
    if result:
        if bcrypt.check_password_hash(result[0]['password'], request.form['pass']):
            session['user_id'] = result[0]['user_id']
            session["successMessage"] = "WELCOME"            
            return redirect("/wallpage")
    flash("you could not be logged in")
    return redirect("/")


#messaging


@app.route("/send", methods=['POST'])
def messages():
    if len(request.form['messages']) < 5:
        flash('message should be more than 4 charcters')
        return redirect("/wallpage")
    else:
      
        mysql = connectToMySQL("private")
        query= "INSERT INTO messages (messages, user_id, recipient_id) VALUES (%(fn)s, %(id)s, %(rec_id)s);"
        data= {
            'fn': request.form['messages'],
            'id': session['user_id'],
            'rec_id': request.form['recipient_id']
                
        }
        mysql.query_db(query, data)
        print(request.form)
        return redirect('/wallpage')

@app.route('/delete/<id>')
def delete(id):
        mysql = connectToMySQL("private")
        query = "DELETE FROM messages WHERE id=%(id)s;"
        data= {
            "id":id,
        }
        mysql.query_db(query, data)
       
        return redirect('/wallpage')







#Log_out Page

@app.route("/logout")
def logout():
    
    session.clear()
    flash("You have been logged out.")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

