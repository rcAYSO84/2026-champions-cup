"""One-time seed of data/games.json from the MatchTrak schedule captured Nov. 2, 2026."""
import json, pathlib

W, Q, S, F = "Wildcard", "Quarterfinal", "Semifinal", "Final"
SS1, SS2 = "World Cup SS1", "World Cup SS2"
YA, YB = "Youth Athletic Park A", "Youth Athletic Park B"
BB, GL = "Beebe", "Gilleran 1"
FIN = "Semifinal winners"

G = [
 # BU09
 (30038,"BU09","2026-11-02","18:45",W,"Vega","Rathburn",SS2),
 (30039,"BU09","2026-11-05","17:30",Q+" 1","Call","Vega/Rathburn winner",SS2),
 (30042,"BU09","2026-11-05","17:30",Q+" 4","Spanos","Venanzi",SS1),
 (30040,"BU09","2026-11-05","18:45",Q+" 2","Low","Larason",SS2),
 (30041,"BU09","2026-11-05","18:45",Q+" 3","Tarpley","Digiambattista",SS1),
 (30043,"BU09","2026-11-09","18:45",S,"Winner QF1","Winner QF4",SS1),
 (30044,"BU09","2026-11-09","18:45",S,"Winner QF2","Winner QF3",SS2),
 (30045,"BU09","2026-11-11","18:45",F,FIN,"",SS1),
 # BU10
 (30054,"BU10","2026-11-02","17:30",W,"Ezzati","Casey",SS1),
 (30055,"BU10","2026-11-04","17:30",Q+" 1","Alduenda","Ezzati/Casey winner",SS2),
 (30058,"BU10","2026-11-04","17:30",Q+" 4","Zaccuri","Amaro",SS1),
 (30056,"BU10","2026-11-04","18:45",Q+" 2","Henderson","Eckhardt",SS2),
 (30057,"BU10","2026-11-04","18:45",Q+" 3","Herman","Rummel",SS1),
 (30059,"BU10","2026-11-10","17:30",S,"Winner QF1","Winner QF4",SS1),
 (30060,"BU10","2026-11-10","17:30",S,"Winner QF2","Winner QF3",SS2),
 (30061,"BU10","2026-11-12","17:30",F,FIN,"",SS1),
 # BU12
 (30069,"BU12","2026-11-03","17:30",W,"Pregizer","Froehlich",YA),
 (30067,"BU12","2026-11-03","19:00",W,"Ortiz","Ballon",BB),
 (30070,"BU12","2026-11-03","19:00",W,"Matranga","De Angelis",YA),
 (30072,"BU12","2026-11-05","17:30",Q+" 2","Henderson","Matranga/De Angelis winner",BB),
 (30073,"BU12","2026-11-05","17:30",Q+" 3","Brissinger","Ortiz/Ballon winner",YA),
 (30071,"BU12","2026-11-05","19:00",Q+" 1","Sweeney","Pregizer/Froehlich winner",BB),
 (30074,"BU12","2026-11-05","19:00",Q+" 4","Taylor","Casey",YA),
 (30075,"BU12","2026-11-09","17:30",S,"Winner QF1","Winner QF4",YA),
 (30076,"BU12","2026-11-09","17:30",S,"Winner QF2","Winner QF3",YB),
 (30077,"BU12","2026-11-11","17:30",F,FIN,"",BB),
 # BU14
 (30088,"BU14","2026-11-04","17:30",Q,"Pregizer","Synnott",GL),
 (30089,"BU14","2026-11-04","19:00",Q,"Nicholson","Mueting",GL),
 (30091,"BU14","2026-11-10","17:30",S,"Thresher","Pregizer/Synnott winner",GL),
 (30090,"BU14","2026-11-10","19:00",S,"DeAnda","Nicholson/Mueting winner",GL),
 (30092,"BU14","2026-11-12","17:30",F,FIN,"",GL),
 # GU09
 (30050,"GU09","2026-11-03","17:30",Q,"Tarpley","Fredericksen",SS1),
 (30048,"GU09","2026-11-03","18:45",Q,"Peck","Ford",SS2),
 (30049,"GU09","2026-11-03","18:45",Q,"Cabodi","Poladian-Melzer",SS1),
 (30051,"GU09","2026-11-09","17:30",S,"Gonzalez","Tarpley/Fredericksen winner",SS1),
 (30052,"GU09","2026-11-09","17:30",S,"Peck/Ford winner","Cabodi/Poladian-Melzer winner",SS2),
 (30053,"GU09","2026-11-11","17:30",F,FIN,"",SS1),
 # GU10
 (30063,"GU10","2026-11-02","18:45",Q,"Matranga","Marx",SS1),
 (30064,"GU10","2026-11-10","18:45",S,"McManamy","Matranga/Marx winner",SS1),
 (30065,"GU10","2026-11-10","18:45",S,"Cornish","Cohen",SS2),
 (30066,"GU10","2026-11-12","18:45",F,FIN,"",SS1),
 # GU12
 (30078,"GU12","2026-11-02","17:30",W,"Bartczak","Cassuto",BB),
 (30079,"GU12","2026-11-02","19:00",W,"Benavides Zacarias","Cohen",BB),
 (30081,"GU12","2026-11-04","17:30",Q+" 2","Cappelletti","Bartczak/Cassuto winner",BB),
 (30082,"GU12","2026-11-04","17:30",Q+" 3","Williams","Fredericksen",YA),
 (30080,"GU12","2026-11-04","19:00",Q+" 1","Johnson","Benavides Zacarias/Cohen winner",BB),
 (30083,"GU12","2026-11-04","19:00",Q+" 4","Deschenes","Thurlow",YA),
 (30084,"GU12","2026-11-09","19:00",S,"Winner QF1","Winner QF4",YA),
 (30085,"GU12","2026-11-09","19:00",S,"Winner QF2","Winner QF3",YB),
 (30086,"GU12","2026-11-11","19:00",F,FIN,"",BB),
 # GU14
 (30093,"GU14","2026-11-03","17:30",S,"Jones","Synnott",GL),
 (30094,"GU14","2026-11-03","19:00",S,"Gardner","Vega",GL),
 (30095,"GU14","2026-11-12","19:00",F,FIN,"",GL),
]

games = [dict(id=g[0], div=g[1], date=g[2], time=g[3], round=g[4], home=g[5], away=g[6],
              field=g[7], home_score=None, away_score=None, note="") for g in G]
out = {"updated": "2026-11-02T07:00:00-08:00", "games": games}
p = pathlib.Path(__file__).resolve().parent.parent / "data" / "games.json"
p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(games), "games")
