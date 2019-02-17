import math
import pygame   # za grafiku
import serial   # za komunikaciju preko serijskog porta
import sys      # omogucava pristup nekim promenljivama koje koristi ili odrzava prevodilac
                # i funkcijama koje snazno komuniciraju sa prevodiocem
from pygame.locals import *

# inicijalizujemo pygame, odnosno kanvas na kome cemo iscrtavati
pygame.init()
# visina i sirina se mogu menjati i to nece uticati na crtanje 
width  = 700
height = 700
# u svim funkcijama za crtanje u pygamu, uvek se prvo podesava sirina pa visina
canvas = pygame.display.set_mode((width,height))
# inicijalizujemo promenljivu koja ce sluziti za citanje sa serijskog porta
ser = serial.Serial()
# parametar timeout oznacava na koliko sekundi citamo sa serijskog porta
# ukoliko je potreban broj bajtova ispunjen, ne ceka se 1 sekunda vec se vrednost automatski cita
ser.timeout = 1
# ime porta na kome je arduino
ser.port = 'com3' 
ser.open()
# definisemo boje
white = (255,255,255)
black = (0,0,0)
green = (0,255,0)
red   = (255,0,0)
# lista u kojoj cemo cuvati detektovane tacke
points= []

# funkcija kojom vrsimo konverziju iz stepena u radijane
def to_radian(angle):
    # po formuli za konverziju iz radijana u stepene
    return((angle*3.14)/180)

# funkcija detected se poziva kako bi vratila poziciju na kojoj se nalazi detektovani objekat
# kao parametri se prosledjuju koordinate koje zavise od ugla i daljine
def detected(x,y):
    _x = int(x) + width//2
    _y = height//2 - int(y)
    # vracamo dimenzije u obliku niza
    return([_x,_y])

# funkcija kojom pravimo listu u kojoj cuvamo pozicije detektovanih objakata
def add_points(angle,distance):
    # globalne promenljive se mogu modifikovati i van opsega funkcije u kojoj su definisane
    global points
    distance *= 10
    x = math.cos(to_radian(angle))*distance
    y = math.sin(to_radian(angle))*distance
    position = detected(x,y)
    # promeljiva pos ce nakon izvrsavanja prethodnih instrukcija sadrzati koordinate tacke koja predstavlja detekovani objekat
    # ovu vrednost dodajemo u listu tacaka
    points.append(position)

# servo motor koji je koriscen u ovom projektu se moze kretati od 0 do 179 stepni, pa cemo u cilju lepseg iscrtavanja
# prekriti donji deo kruga i ispasti neki tekst
def draw_rect():
    pygame.draw.rect(canvas,green,(0,0,width,height//2+10),5)
    pygame.draw.rect(canvas,black,(0,height//2+10,width,height//2+10),0)     

    _font = pygame.font.Font('freesansbold.ttf',32)
    _text = _font.render("Projekat iz predmeta", True,(255,255,255))
    canvas.blit(_text,(width//2-150,height//2+100))
    _text = _font.render("Senzorski Sistemi", True,(255,255,255))
    canvas.blit(_text,(width//2-150,height//2+150))
    _text = _font.render("Davor Jordačević", True,(255,255,255))
    canvas.blit(_text,(width//2-150,height//2+200))

# draw_cricles koristimo za crtanje koncetricnih krugova
def draw_circles(disp=canvas):
    radius = 50
    # koncetricni krugovi ce imati isti centar, a to je polovina sirine i visine kanvasa podeljeno sa 2
    for x in range(1,width//2):
        new_radius = ((x//radius)+1)*radius
        pygame.draw.circle(disp,green,(width//2,height//2),new_radius,2)
    draw_rect()
   
# draw_points korisitmo za crtanje tacke na kojoj se nalazi detektovani objekat
def draw_points(list_points,disp=canvas):
    # za svaku tacku u listi iscrtavamo krug oko te tacke
    for point in list_points:
        pygame.draw.circle(disp,red,point,3)

# draw_line se koristi za crtanje linije radara koje ce se kretati u zavisiti od polozaja motora i senzora
def draw_line(angle,disp=canvas):
    a = math.tan(to_radian(angle))
    y = height//2
    if a==0:
        y = 0
        x = width/2 if angle ==0 else -width/2 if angle==180 else x
    else:
        x = y//a
    position = detected(x,y)
    pygame.draw.line(disp,green,(width/2,height/2),position,2)

# funkcijom read sa serijskog porta na kome se nalazi arduino citamo vrednosti ugla i daljine detektovanog objekta
def read(ser):
    # citanje podatka za serijskog porta
    angle_distance = ser.readline()
    # decodovanje vrsimo prebacivanje iz bytova u asci karaktere
    angle_distance = angle_distance.decode()
    # nakon dekodovanja potrebno je podeliti procitanu sekvencu
    # prvo uklanjamo poslednja dva karaktera kako bi izbegli rad sa float vrednostima
    angle_distance = angle_distance[:len(angle_distance)-2]
    # nakon toga od stringa koji je sadrzao dva broja podeljena ; pravimo niz od ta dva broja
    angle_distance = angle_distance.split(";")
    # proveravamo da li je duzina niza razlicita od dva, ili sadrzi prazno mesto i ako jeste vracamo false,
    # u suprotnom funkcija vraca sam niz
    if len(angle_distance)!=2 or ("" in angle_distance):
        return(False)
    return(angle_distance)

# ispisujemo tekst sa daljinom detektovanog objekta
def draw_text(canvas,text,text_size):
    # definisemo font i velicinu fonta
    # freesansbold.ttf je jedini font koji dolazi uz pygame.font.Font, ostale fontove je potrebno dodatno preuzeti
    _font = pygame.font.Font('freesansbold.ttf',text_size)
    # definisemo tekst koji se ispisuje, kao i njegovu boju
    _text = _font.render(text, True,white)
    canvas.blit(_text,(8,8))
        
# u beskonacnoj while petlji iscrtavamo
#   kanvas,
#   koncentricne krugove,
#   liniju,
#   kao i detektovane objekte.
while True:
    # popunjavamo kanvas crnom bojom
    canvas.fill(black)
    # nakon cega citamo podatke sa serijskog porta
    angle_dist= read(ser)
    # ukoliko su podaci dobro procitani, nastavljamo sa programom
    if angle_dist==False: 
        continue
    # iz liste uzimamo podatke i upisujemo ih u promelnjive angle i distance
    angle= float(angle_dist[0])
    dist=  float(angle_dist[1])
    # ukoliko je ugao 0 ili 180, praznimo listu kako se u sledecem skeniranju ne bi
    # ponovile prethodno procitane vrednosti
    points = [] if angle==0 or angle==180 else points
    # iscrtavamo krugove
    draw_circles(canvas)
    # iscrtavamo liniju pod odredjenim ugolom
    draw_line(angle)
    # dodajemo detektovane objekte u listu
    add_points(angle,dist)
    # iscrtavamo tacke iz liste
    draw_points(points)
    # ispisujemo tekst sa informacijama o uglu i daljini
    draw_text(canvas,"Angle = "+str(angle)+", Distance = "+str(dist),15)
    # bitno je proveravati i stanje pygame displeja
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    # ukoliko ne dodje do prekida, potrebno je updejtovati trenutno stanje displeja
    pygame.display.update()
