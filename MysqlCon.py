import pymysql.cursors
import sys

class MysqlCon:
    def __init__(self, id):
        # Make a connection with the Mysql server
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password='',
                                          db='rowcoaches',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor);
        self.cursor = self.connection.cursor();
        self.regattaId = id;
        
    def getAll(self):
        res = [];
        for result in self.cursor.fetchall():
            res.append(result);
        return res;
        
    def getRegattaInfo(self):
        sql = "SELECT * FROM `regatta` WHERE `id` = '%s'";
        self.cursor.execute(sql, (self.regattaId,));
        result = self.cursor.fetchone();
        return result;
   
    def getDevisions(self):
        sql = "SELECT DISTINCT(event.Devision) as Name FROM `event` INNER JOIN `regatta_to_event` ON regatta_to_event.EventId = event.Id INNER JOIN `regatta` ON regatta.Id = regatta_to_event.RegattaId WHERE regatta.Id = %s";
        self.cursor.execute(sql, (self.regattaId,));
        return self.getAll();
    
    def getNumbers(self):
        sql = "SELECT DISTINCT(event.Number) as Name FROM `event` INNER JOIN `regatta_to_event` ON regatta_to_event.EventId = event.Id INNER JOIN `regatta` ON regatta.Id = regatta_to_event.RegattaId WHERE regatta.Id = %s";
        self.cursor.execute(sql, (self.regattaId,));
        return self.getAll();
    
    def getEvents(self):
        devisions = self.getDevisions();
        res = {};
        sql = "SELECT event.* FROM `event` INNER JOIN `regatta_to_event` ON regatta_to_event.EventId = event.Id INNER JOIN `regatta` ON regatta.Id = regatta_to_event.RegattaId WHERE regatta.Id = %s AND event.Devision = %s";
        for i in range(0, len(devisions)):
            self.cursor.execute(sql, (self.regattaId, str(devisions[i]['Name']),));
            print(devisions[i]['Name'], file=sys.stderr)
            res[devisions[i]['Name']] = {};
            for result in self.cursor.fetchall():
                res[devisions[i]['Name']][result['Number']] = result;
        return res;
    
    def getEventDetails(self, num):
        sql = "SELECT event.* FROM `event` INNER JOIN `regatta_to_event` ON regatta_to_event.EventId = event.Id WHERE regatta_to_event.RegattaId = %s AND event.Num = %s";
        self.cursor.execute(sql, (self.regattaId, num))
        return self.getAll();
    
    def getHeatsFromEvent(self, event):
        sql = "SELECT heat.* FROM `heat` INNER JOIN `event_to_heat` ON event_to_heat.HeatId = heat.Id INNER JOIN regatta_to_event ON event_to_heat.EventId = regatta_to_event.EventId WHERE regatta_to_event.RegattaId = %s AND event_to_heat.EventId = %s";
        self.cursor.execute(sql, (self.regattaId, event))
        heats = self.getAll();
        for heat in heats:
            sql = "SELECT crew.*, heat_to_crew.Lane as Lane, heat_to_crew.Pos as Pos FROM `crew` INNER JOIN `heat_to_crew` ON crew.Id = heat_to_crew.CrewId WHERE heat_to_crew.HeatId = %s"
            self.cursor.execute(sql, heat['Id']);
            heat['Crews'] = self.getAll()
        return heats;
    
    def getClubs(self):
        sql = "SELECT DISTINCT(crew.Ver) as Vern, crew.Club as Club, (SELECT Count(*) FROM crew WHERE `Ver` = Vern) as Inschrijvingen FROM `crew` INNER JOIN `event_to_crew` ON crew.Id = event_to_crew.CrewId INNER JOIN `event` ON event_to_crew.EventId = event.Id INNER JOIN `regatta_to_event` ON regatta_to_event.EventId = event.Id INNER JOIN `regatta` ON regatta.Id = regatta_to_event.RegattaId WHERE regatta.Id = %s";
        self.cursor.execute(sql, (self.regattaId))
        return self.getAll();
    
    def getClubDetails(self, club):
        sql = "SELECT crew.Ver as Ver, crew.Club as Club, crew.Name as Name FROM `crew` INNER JOIN `event_to_crew` ON crew.Id = event_to_crew.CrewId INNER JOIN `event` ON event_to_crew.EventId = event.Id INNER JOIN `regatta_to_event` ON regatta_to_event.EventId = event.Id INNER JOIN `regatta` ON regatta.Id = regatta_to_event.RegattaId WHERE regatta.Id = %s AND crew.Ver = %s";
        self.cursor.execute(sql, (self.regattaId, club))
        return self.getAll();
    
    def getTrackers(self):
        sql = "SELECT tracker.Id as Id, (CASE WHEN (Crew = '0') THEN 'Nobody' ELSE crew.Name End) as Crew FROM tracker LEFT JOIN crew ON crew.Id = tracker.Crew";
        self.cursor.execute(sql)
        return self.getAll();
    
    def getCrews(self, trackerId):
        sql = "SELECT crew.* FROM crew WHERE Id NOT IN (SELECT Crew FROM tracker)";
        self.cursor.execute(sql)
        return self.getAll();
    
    def assignTracker(self, tracker, crew):
        sql = "UPDATE `tracker` SET `Crew` = %s WHERE `Id`= %s";
        self.cursor.execute(sql, (crew, tracker));
        return;
    
    def clearTracker(self,id):
        sql = "UPDATE `tracker` SET `Crew` = '0' WHERE `Id` = %s";
        self.cursor.execute(sql, id);
        return;
      