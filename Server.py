from flask import Flask
from flask import jsonify, render_template, request, url_for
from multiprocessing import Process, Queue, cpu_count
import time;
import serial;
import sys;
import struct;
from datetime import datetime, date
from locale import setlocale, LC_ALL, locale_alias

from SerialCon import SerialCon
from MysqlCon import MysqlCon
from Race import Race

global q;
global Con;
global Serial;
global Race;

RegattaId = 1; #Damen Raceroei Regatta
Con = MysqlCon(RegattaId);
Serial = SerialCon();
Race = Race(Con);

app = Flask(__name__) # Start the web application.

@app.context_processor
def inject_regatta():
    global Con;
    return dict(regatta=Con.getRegattaInfo());
    

@app.route('/') # This is the main view which is shown to the onlookers.
def index():
    return render_template('index.html')

@app.route('/_start_serial/') # Start the serial connection with the arduino
def start_serial():
    global Serial;
    Serial.connect("COM5");

@app.route('/_get_race_status/') # Check whether there is currently a race busy
def get_race_status():
    global Race;
    if (Race.get_race_status()):
        return jsonify(result=True);
    else:
        # Check when the next race is going to start
        return jsonify(time=Race.get_next_race());
    
   
@app.route('/admin/') # This page allows the competition crew to view what's going on.
def admin():
    global Con;
    Devisions = Con.getDevisions();
    Numbers = Con.getNumbers();
    Events = Con.getEvents();
    return render_template('admin.html',
                           devisions=Devisions,
                           numbers=Numbers,
                           events=Events,
                          );
@app.route('/event/')
@app.route('/event/<id>') # Shows specific event information
def event(id=None):
    global Con
    if (id == None):
        return admin();
    Event = Con.getEventDetails(id);
    Heats = Con.getHeatsFromEvent(id);
    return render_template('event.html',
                           event = Event[0],
                           heats = Heats,
                               );

@app.route('/clubs/')
@app.route('/clubs/<id>') # Shows specific club information
def crew(id=None):
    global Con
    if (id == None):
        Clubs = Con.getClubs();
        return render_template('clubs.html',
                               clubs = Clubs,
                               );
    else:
        ClubDetails = Con.getClubDetails(id);
        return render_template('clubdetails.html',
                               club=ClubDetails,
                               );

@app.route('/trackers/')
@app.route('/trackers/<id>') # View all trackers or assign one to a crew
def trackers(id=None):
    global Con
    if (id == None):
        Trackers = Con.getTrackers();
        return render_template('trackers.html',
                               trackers=Trackers,
                               );

@app.route('/assign_tracker/')
@app.route('/assign_tracker/<id>')
@app.route('/assign_tracker/<id>/<crew>') # Assign a tracker to a crew.
def assign_tracker(id=None, crew=None):
    global Con
    if (crew != None):
        Con.assignTracker(id, crew);
        return trackers();
    if (id == None):
        return trackers();
    if (crew == None):
        return render_template('assign_tracker.html',
                           tracker_id = id,
                           crews = Con.getCrews(id),
                           );
@app.route('/clear_tracker/')
@app.route('/clear_tracker/<id>')
def clear_tracker(id=None):
    global Con
    if (id != None):
        Con.clearTracker(id);
    return trackers();

@app.route('/track/')
@app.route('/track/<id>')
def track(id=None):
    if (id == None):
        return trackers();
    return render_template('track.html',
                           tracker_id = id,
                           );
          
# Jinja functions
@app.template_filter('datetime')
def format_datetime(s):
    setlocale(LC_ALL, "nld");
    return s.strftime("%A").capitalize();

@app.template_filter('timehm')
def format_time(s):
    return ':'.join(str(s).split(':')[:2])
    

q  = Queue();
trackers = [];
for i in range(0,60):
    nulstate = {"Unit": i+1, "Stroke": 0, "Split": 0, "Direction":0, "Long": 0, "Lat": 0, "Last": 0};
    trackers.append(nulstate);
@app.route('/_return_trace/')
@app.route('/_return_trace/<id>')
def return_trace(id = None):
    if (id == None):
        return jsonify(result=False);
    global q;
    global trackers
    while (not q.empty()):
        print("Getting", file=sys.stderr);
        trace = q.get();
        unit = int(trace['Unit']);
        trackers[unit-1] = trace;
        trackers[unit-1]['Time'] = str(trackers[unit-1]['Time']);
    return jsonify(result=trackers[int(id)]);

def packetFunction(packet):
    # Check if the length is good
    if (packet[2] != len(packet)):
        return False;
    else:
        # Remove the double zeros
        cpacket = [];
        a = False;
        for i in range(3, packet[2]-2):
            if (packet[i] == 1 and a == False):
                a = True;
            else:
                cpacket.append(packet[i])
                a = False;
        checksum = 0;
        for i in range(1, len(cpacket)):
            checksum += cpacket[i];
        checksum = checksum % 255;
        if (checksum == 0):
            checksum = 1;
        if (checksum != cpacket[0]):
            return False;
        else:
        		
            print(cpacket, file=sys.stderr);
            Unit      = cpacket[1];
            ConState  = cpacket[2];
            Stroke    = cpacket[3];
            Split     = cpacket[4];
            byteLot   = [];
            byteLat   = [];
            byteDir   = [];
            for i in range(0,4):
                byteLot.append(cpacket[5+i])
                byteLat.append(cpacket[9+i]);
                byteDir.append(cpacket[13+i]);
            bLong = bytearray();
            bLat  = bytearray();
            bDir  = bytearray();
            bLong.extend(byteLot);
            bLat.extend(byteLat);
            bDir.extend(byteDir);
            Longitude = struct.unpack("<f", bLong);
            Latitude  = struct.unpack("<f", bLat);
            Direction = struct.unpack("<f", bDir);
            data = {
                "Unit": Unit,
                "Stroke": Stroke,
                "Split": Split,
                "Direction": Direction,
                "Long": Longitude,
                "Lat": Latitude,
                "Time": datetime.now().time(),
            };
            return data;

def workerFunction(q2): # This function controls the workers and defines what they should do
    Serial.listen();
    
    packet = [];
    listening = False;
    buffer = [];
    i = 0;
    return;
    while (1):
        while(ser.inWaiting()):
            c = ord(ser.read());
            buffer.append(c);
            i = i + 1;
            if (i > 1):
                if (listening):
                    packet.append(c);
                    if (buffer[i-1] == 3 and buffer[i-2] == 1): # We have a complete packet
                        # Check the checksum etc - Push to function
                        print(packet, file=sys.stderr);
                        check = packetFunction(packet);
                        if (check != False):
                            q2.put(check);
                        j = 0;
                        i = 0;
                        buffer[:] = [];
                        packet[:] = [];
                        listening = False;
                else:
                    if (buffer[i-1] == 2 and buffer[i-2] == 1): # We have a packet start
                        packet.append(1);
                        packet.append(2);
                        listening = True;
        time.sleep(0.01);

if __name__ == '__main__': # This makes sure that we only run the host once.
    # Create a worker which will deal with the serial connecton
    Worker = Process(target=workerFunction, args=(q,));
    Worker.start();
    app.run(debug=True);