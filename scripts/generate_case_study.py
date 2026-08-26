from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / 'HORMONA-Case-Study-Assa-Traore.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)

W, H = A4

# Palette: premium / health / consulting
INK = HexColor('#17212B')
MUTED = HexColor('#61707F')
IVORY = HexColor('#F8F5F0')
WHITE = HexColor('#FFFFFF')
TEAL = HexColor('#0B6B67')
TEAL_DARK = HexColor('#084B48')
SAGE = HexColor('#DDEAE5')
LILAC = HexColor('#E8E0F2')
ROSE = HexColor('#F3E2E5')
GOLD = HexColor('#C8A96B')
LINE = HexColor('#D9DEE3')
SOFT = HexColor('#F1F3F5')

FONT = 'Helvetica'
FONT_B = 'Helvetica-Bold'
FONT_I = 'Helvetica-Oblique'


def set_fill(c, color):
    c.setFillColor(color)


def rounded_rect(c, x, y, w, h, r=10, fill=WHITE, stroke=None, sw=1):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
        stroke_flag = 1
    else:
        stroke_flag = 0
    c.roundRect(x, y, w, h, r, fill=1 if fill is not None else 0, stroke=stroke_flag)
    c.restoreState()


def line(c, x1, y1, x2, y2, color=LINE, sw=1):
    c.saveState(); c.setStrokeColor(color); c.setLineWidth(sw); c.line(x1,y1,x2,y2); c.restoreState()


def wrap_lines(text, font, size, max_width):
    words = text.split()
    lines = []
    current = ''
    for word in words:
        test = word if not current else current + ' ' + word
        if stringWidth(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text(c, text, x, y, max_width, font=FONT, size=10, color=INK, leading=None, max_lines=None):
    leading = leading or size * 1.35
    c.setFont(font, size)
    c.setFillColor(color)
    lines = []
    for para in text.split('\n'):
        if para == '':
            lines.append('')
        else:
            lines.extend(wrap_lines(para, font, size, max_width))
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            last = lines[-1]
            while stringWidth(last + '...', font, size) > max_width and last:
                last = last[:-1]
            lines[-1] = last.rstrip() + '...'
    ty = y
    for ln in lines:
        c.drawString(x, ty, ln)
        ty -= leading
    return ty


def draw_bullets(c, items, x, y, max_width, size=9.5, color=INK, bullet_color=TEAL, gap=4):
    cy = y
    for item in items:
        c.setFillColor(bullet_color)
        c.circle(x+3, cy+3, 2, fill=1, stroke=0)
        cy = draw_text(c, item, x+14, cy, max_width-14, size=size, color=color, leading=size*1.35)
        cy -= gap
    return cy


def title(c, kicker, heading, sub=None):
    c.setFillColor(TEAL)
    c.setFont(FONT_B, 9)
    c.drawString(22*mm, H-23*mm, kicker.upper())
    c.setFillColor(INK)
    heading_size = 23
    max_heading_width = W - 44*mm
    while heading_size > 15 and stringWidth(heading, FONT_B, heading_size) > max_heading_width:
        heading_size -= 1
    c.setFont(FONT_B, heading_size)
    c.drawString(22*mm, H-35*mm, heading)
    if sub:
        draw_text(c, sub, 22*mm, H-43*mm, W-44*mm, size=10.5, color=MUTED, leading=14)
    line(c, 22*mm, H-51*mm, W-22*mm, H-51*mm, LINE, 0.8)


def footer(c, page_num):
    line(c, 22*mm, 15*mm, W-22*mm, 15*mm, LINE, 0.7)
    c.setFont(FONT, 7.5); c.setFillColor(MUTED)
    c.drawString(22*mm, 10*mm, 'ASSA TRAORE  |  HORMONA - Market Research & Innovation Strategy')
    c.drawRightString(W-22*mm, 10*mm, f'{page_num:02d}')


def metric(c, x, y, w, h, big, label, fill=SAGE, accent=TEAL):
    rounded_rect(c, x, y, w, h, 12, fill=fill)
    c.setFont(FONT_B, 21); c.setFillColor(accent); c.drawString(x+12, y+h-28, big)
    draw_text(c, label, x+12, y+h-44, w-24, size=8.5, color=INK, leading=11)


def section_card(c, x, y, w, h, heading, body, fill=WHITE, accent=TEAL, bullets=None):
    rounded_rect(c, x, y, w, h, 10, fill=fill, stroke=LINE, sw=0.7)
    c.setFillColor(accent); c.setFont(FONT_B, 10.5); c.drawString(x+12, y+h-20, heading)
    if bullets:
        draw_bullets(c, bullets, x+12, y+h-38, w-24, size=8.5)
    else:
        draw_text(c, body, x+12, y+h-38, w-24, size=8.7, color=INK, leading=11.5)


def pill(c, x, y, text, fill=SAGE, color=TEAL_DARK):
    fs = 7.5
    tw = stringWidth(text, FONT_B, fs) + 16
    rounded_rect(c, x, y, tw, 18, 9, fill=fill)
    c.setFillColor(color); c.setFont(FONT_B, fs); c.drawCentredString(x+tw/2, y+6, text)
    return tw


def arrow(c, x1, y1, x2, y2, color=TEAL, sw=1.6):
    c.saveState(); c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(sw)
    c.line(x1,y1,x2,y2)
    ang = math.atan2(y2-y1, x2-x1)
    ah = 7
    for a in [ang+2.6, ang-2.6]:
        c.line(x2, y2, x2+ah*math.cos(a), y2+ah*math.sin(a))
    c.restoreState()


def page_cover(c):
    c.setFillColor(IVORY); c.rect(0,0,W,H,fill=1,stroke=0)
    # decorative circles
    c.setFillColor(SAGE); c.circle(W-25*mm, H-34*mm, 25*mm, fill=1, stroke=0)
    c.setFillColor(LILAC); c.circle(W-9*mm, H-18*mm, 14*mm, fill=1, stroke=0)
    c.setFillColor(ROSE); c.circle(22*mm, 24*mm, 17*mm, fill=1, stroke=0)

    c.setFillColor(TEAL); c.setFont(FONT_B, 9); c.drawString(24*mm, H-34*mm, 'CASE STUDY  /  PORTFOLIO 2026')
    c.setFillColor(INK); c.setFont(FONT_B, 40); c.drawString(24*mm, H-63*mm, 'HORMONA')
    c.setFont(FONT_B, 18); c.setFillColor(TEAL_DARK); c.drawString(24*mm, H-78*mm, 'Market Research & Innovation Strategy')
    draw_text(c, 'Etude de marche, innovation FemTech et recherche utilisateur autour d\'un concept de patch hormonal connecte associe a une application mobile.', 24*mm, H-93*mm, 140*mm, size=11, color=MUTED, leading=15)

    # central concept card
    rounded_rect(c, 24*mm, H-176*mm, 162*mm, 62*mm, 14, fill=WHITE, stroke=LINE, sw=0.8)
    c.setFillColor(TEAL); c.setFont(FONT_B, 10); c.drawString(34*mm, H-132*mm, 'CONCEPT')
    c.setFillColor(INK); c.setFont(FONT_B, 16); c.drawString(34*mm, H-147*mm, 'Patch connecte  +  Application mobile')
    draw_text(c, 'Objectif : explorer la pertinence du concept, son potentiel de marche, les attentes des utilisatrices et les principaux freins a son adoption.', 34*mm, H-158*mm, 142*mm, size=9.3, color=MUTED, leading=12.5)

    # skill tags
    x = 24*mm; y = 67*mm
    for t in ['Market Research','Benchmark','User Research','Strategy','Innovation']:
        w = pill(c,x,y,t,fill=SAGE if t!='Innovation' else LILAC)
        x += w + 6
        if x > W-55*mm:
            x = 24*mm; y -= 24

    c.setFillColor(INK); c.setFont(FONT_B, 12); c.drawString(24*mm, 33*mm, 'Assa TRAORE')
    c.setFillColor(MUTED); c.setFont(FONT, 9); c.drawString(24*mm, 27*mm, 'Mastere 2 - Entrepreneuriat, Management de Projet & Consulting | ESGCI Paris')
    c.setFillColor(TEAL); c.setFont(FONT_B, 8); c.drawRightString(W-24*mm, 27*mm, 'github.com/AssaT17')


def page_context(c):
    title(c, '01 - CONTEXTE', 'Du besoin utilisateur a une opportunite FemTech', 'Le projet part d\'un constat : les troubles hormonaux peuvent affecter fortement le quotidien, alors que le suivi disponible reste souvent ponctuel ou declaratif.')
    y0 = H-69*mm
    metric(c, 22*mm, y0-38*mm, 50*mm, 31*mm, '1 / 10', 'SOPK - chiffre utilise dans l\'etude academique')
    metric(c, 80*mm, y0-38*mm, 50*mm, 31*mm, '1 / 10', 'Endometriose - chiffre utilise dans l\'etude academique', fill=ROSE, accent=HexColor('#9C4F63'))
    metric(c, 138*mm, y0-38*mm, 50*mm, 31*mm, '14 M', 'Femmes menopausees ou perimenopausees en France - etude', fill=LILAC, accent=HexColor('#6A4C91'))

    section_card(c,22*mm,85*mm,78*mm,67*mm,'PROBLEMATIQUE','',fill=WHITE,bullets=[
        'Comment rendre les variations hormonales plus comprehensibles au quotidien ?',
        'Comment associer technologie, personnalisation et accompagnement sans complexifier l\'usage ?',
        'Comment instaurer confiance et credibilite autour de donnees de sante sensibles ?'])
    section_card(c,110*mm,85*mm,78*mm,67*mm,'CIBLES ETUDIEES','',fill=WHITE,accent=HexColor('#6A4C91'),bullets=[
        'Femmes souhaitant mieux comprendre leur cycle',
        'Femmes concernees par SOPK, endometriose ou fertilite',
        'Femmes en periode de menopause',
        'Utilisatrices de solutions numeriques de suivi sante'])
    footer(c,2)


def page_concept(c):
    title(c, '02 - CONCEPT', 'HORMONA : connecter la donnee au quotidien', 'Une proposition de valeur reposant sur la complementarite d\'un capteur physique et d\'une experience mobile claire.')

    # Left patch illustration
    rounded_rect(c, 22*mm, 98*mm, 70*mm, 95*mm, 14, fill=SAGE)
    c.setFillColor(WHITE); c.circle(57*mm, 153*mm, 22*mm, fill=1, stroke=0)
    c.setStrokeColor(TEAL); c.setLineWidth(2); c.circle(57*mm,153*mm,14*mm,fill=0,stroke=1)
    c.setFillColor(TEAL); c.setFont(FONT_B, 9); c.drawCentredString(57*mm,151*mm,'PATCH')
    c.setFillColor(INK); c.setFont(FONT_B, 13); c.drawString(32*mm,118*mm,'Patch cutane connecte')
    draw_text(c,'Discret, confortable et pense pour transmettre des donnees vers l\'application via connectivite sans fil.',32*mm,109*mm,50*mm,size=8.8,color=MUTED,leading=11.5)

    # Right app illustration
    rounded_rect(c, 118*mm, 98*mm, 70*mm, 95*mm, 14, fill=LILAC)
    rounded_rect(c, 140*mm, 122*mm, 28*mm, 56*mm, 8, fill=INK)
    rounded_rect(c, 143*mm, 126*mm, 22*mm, 48*mm, 5, fill=WHITE)
    c.setFillColor(TEAL); c.circle(154*mm,162*mm,4*mm,fill=1,stroke=0)
    line(c,146*mm,150*mm,162*mm,150*mm,TEAL,1.2)
    line(c,146*mm,143*mm,160*mm,143*mm,HexColor('#B2BBC4'),1)
    line(c,146*mm,136*mm,158*mm,136*mm,HexColor('#B2BBC4'),1)
    c.setFillColor(INK); c.setFont(FONT_B, 13); c.drawString(128*mm,118*mm,'Application mobile')
    draw_text(c,'Visualisation, suivi, alertes, conseils personnalises et interpretation simple des variations.',128*mm,109*mm,50*mm,size=8.8,color=MUTED,leading=11.5)

    arrow(c,95*mm,146*mm,114*mm,146*mm,TEAL,2)

    # benefits strip
    rounded_rect(c,22*mm,52*mm,166*mm,32*mm,10,fill=WHITE,stroke=LINE,sw=0.8)
    labels=[('Suivre','cycle et variations'),('Comprendre','signaux du corps'),('Anticiper','periodes sensibles'),('Adapter','nutrition, sport, repos')]
    x=27*mm
    for i,(a,b) in enumerate(labels):
        if i: line(c,x-5*mm,58*mm,x-5*mm,78*mm,LINE,0.8)
        c.setFillColor(TEAL); c.setFont(FONT_B,10); c.drawString(x,70*mm,a)
        c.setFillColor(MUTED); c.setFont(FONT,7.7); c.drawString(x,63*mm,b)
        x += 40*mm
    footer(c,3)


def page_market(c):
    title(c, '03 - MARCHE', 'Un environnement porteur mais exigeant', 'L\'etude combine donnees de marche, tendances de consommation et contraintes de mise sur le marche.')
    # Metrics from project source, clearly labelled
    metric(c,22*mm,154*mm,78*mm,34*mm,'16 Md$', 'Marche mondial des patchs cutanes electroniques en 2025 - chiffre repris de l\'etude')
    metric(c,110*mm,154*mm,78*mm,34*mm,'4,1 Md$', 'Marche mondial des applications de sante feminine en 2024 - chiffre repris de l\'etude',fill=LILAC,accent=HexColor('#6A4C91'))

    section_card(c,22*mm,88*mm,78*mm,54*mm,'MOTEURS DE CROISSANCE','',bullets=[
        'Sensibilisation accrue a la sante feminine',
        'Digitalisation des parcours de sante',
        'Essor des wearables et biocapteurs',
        'Recherche de solutions personnalisees'])
    section_card(c,110*mm,88*mm,78*mm,54*mm,'POINTS DE VIGILANCE','',accent=HexColor('#9C4F63'),bullets=[
        'Validation clinique et credibilite scientifique',
        'RGPD et protection des donnees sensibles',
        'Couts de R&D et miniaturisation',
        'Acceptabilite prix / usage'])

    # simple opportunity matrix
    c.setFillColor(INK); c.setFont(FONT_B,10.5); c.drawString(22*mm,73*mm,'Lecture strategique')
    rounded_rect(c,22*mm,38*mm,166*mm,28*mm,10,fill=SOFT)
    items=['FemTech en croissance','Besoin de confiance','Technologie differenciante','Marche encore en structuration']
    x=28*mm
    fills=[SAGE,ROSE,LILAC,IVORY]
    for i,it in enumerate(items):
        w=pill(c,x,45*mm,it,fill=fills[i],color=INK)
        x += w+5
    footer(c,4)


def page_strategy(c):
    title(c, '04 - ANALYSE STRATEGIQUE', 'PESTEL, opportunites et risques de lancement', 'Le concept se situe a l\'intersection du biomedical, du digital et du bien-etre : sa valeur depend autant de la technologie que du cadre de confiance.')
    # PESTEL 6 cards
    xs=[22,82,142]; ys=[148,91]
    cards=[
        ('POLITIQUE','Politiques de sante publique et reconnaissance croissante des enjeux de sante feminine.',SAGE),
        ('ECONOMIQUE','Demande pour des solutions personnalisees mais pression sur le cout de production.',IVORY),
        ('SOCIOCULTUREL','Interet croissant pour le bien-etre, la prevention et la connaissance de soi.',ROSE),
        ('TECHNOLOGIQUE','Progres des biocapteurs, de la miniaturisation et de l\'analyse predictive.',LILAC),
        ('ECOLOGIQUE','Choix des materiaux, durabilite et reduction des dechets lies aux patchs.',SAGE),
        ('LEGAL','Dispositifs medicaux, protection des donnees, securite et conformite RGPD.',IVORY)]
    idx=0
    for y in ys:
        for x in xs:
            heading,body,fill=cards[idx]; idx+=1
            section_card(c,x*mm,y*mm,50*mm,46*mm,heading,body,fill=fill,accent=TEAL_DARK)

    footer(c,5)


def page_benchmark(c):
    title(c, '05 - BENCHMARK', 'Comprendre les alternatives pour clarifier la difference', 'Quatre references proches ont ete utilisees dans le projet pour comparer technologies, usages et niveaux de proximite avec HORMONA.')

    # table headers
    x0=22*mm; y=180*mm
    widths=[42*mm,58*mm,66*mm]
    headers=['ACTEUR','APPROCHE','LECTURE POUR HORMONA']
    c.setFillColor(TEAL_DARK); c.rect(x0,y,widths[0]+widths[1]+widths[2],12*mm,fill=1,stroke=0)
    xx=x0
    for h,w in zip(headers,widths):
        c.setFillColor(WHITE); c.setFont(FONT_B,7.5); c.drawString(xx+6,y+4*mm,h); xx+=w
    rows=[
        ('Level Zero Health','Suivi hormonal continu via technologie portable.','Tres proche technologiquement; HORMONA cherche une experience plus grand public et quotidienne.'),
        ('Persperity Health','Biosenseur non invasif, notamment autour de l\'estradiol.','Proximite forte; differentiation a construire sur l\'experience, la cible et l\'accompagnement.'),
        ('FemSense','Patch + application base sur la temperature pour la fertilite.','Montre l\'acceptabilite du format patch; HORMONA vise la donnee hormonale directe.'),
        ('Ava','Wearable de suivi de fertilite et indicateurs physiologiques.','Alternative indirecte; confirme l\'interet pour le suivi passif et personnalise.')]
    row_h=34*mm
    cy=y-row_h
    for r_i,row in enumerate(rows):
        fill=WHITE if r_i%2==0 else SOFT
        c.setFillColor(fill); c.rect(x0,cy,sum(widths),row_h,fill=1,stroke=0)
        xx=x0
        for col,(txt,w) in enumerate(zip(row,widths)):
            c.setFillColor(INK if col!=0 else TEAL_DARK)
            f=FONT_B if col==0 else FONT
            draw_text(c,txt,xx+6,cy+row_h-12,w-12,font=f,size=7.8,color=INK if col else TEAL_DARK,leading=10)
            xx+=w
        line(c,x0,cy,x0+sum(widths),cy,LINE,0.6)
        cy-=row_h

    rounded_rect(c,22*mm,32*mm,166*mm,27*mm,10,fill=SAGE)
    c.setFont(FONT_B,10); c.setFillColor(TEAL_DARK); c.drawString(28*mm,49*mm,'DIFFERENCIATION RECHERCHEE')
    c.setFont(FONT,9); c.setFillColor(INK); c.drawString(28*mm,40*mm,'Capteur physique + donnees biologiques + application claire + recommandations personnalisees.')
    footer(c,6)


def page_research(c):
    title(c, '06 - RECHERCHE UTILISATEUR', 'Confronter l\'idee au terrain avant de la valider', 'La phase qualitative explore usages, besoins, freins et perception d\'un dispositif de suivi hormonal continu.')

    # process flow
    steps=[('1','Guide','Questions ouvertes, posture neutre'),('2','Entretiens','Vecu, usages, symptomes, attentes'),('3','Analyse','Verbatims, tendances, divergences'),('4','Synthese','Insights et recommandations')]
    x=22*mm; y=160*mm
    for i,(n,h,b) in enumerate(steps):
        rounded_rect(c,x,y,36*mm,33*mm,10,fill=[SAGE,LILAC,ROSE,IVORY][i],stroke=LINE,sw=0.5)
        c.setFillColor(TEAL_DARK); c.setFont(FONT_B,11); c.drawString(x+7,y+23*mm,n)
        c.setFillColor(INK); c.setFont(FONT_B,9); c.drawString(x+7,y+16*mm,h)
        draw_text(c,b,x+7,y+10*mm,29*mm,size=7.2,color=MUTED,leading=9)
        if i<3: arrow(c,x+37*mm,y+16*mm,x+42*mm,y+16*mm,TEAL,1.3)
        x += 42*mm

    section_card(c,22*mm,83*mm,78*mm,58*mm,'OBJECTIFS DES ENTRETIENS','',bullets=[
        'Comprendre les usages et irritants actuels',
        'Identifier les freins face au patch',
        'Recueillir des suggestions d\'amelioration',
        'Explorer le positionnement et la confiance'])
    section_card(c,110*mm,83*mm,78*mm,58*mm,'COMPETENCES MOBILISEES','',accent=HexColor('#6A4C91'),bullets=[
        'Formulation de questions non orientees',
        'Ecoute active et relance',
        'Analyse de verbatims',
        'Transformation du qualitatif en insights'])

    rounded_rect(c,22*mm,44*mm,166*mm,27*mm,10,fill=SOFT)
    c.setFillColor(INK); c.setFont(FONT_B,9.5); c.drawString(28*mm,60*mm,'POINT DE METHODE')
    draw_text(c,'Les verbatims individuels ne sont pas reproduits dans ce portfolio public afin de proteger la confidentialite et les donnees personnelles des participantes.',28*mm,51*mm,154*mm,size=8.4,color=MUTED,leading=10.5)
    footer(c,7)


def page_insights(c):
    title(c, '07 - INSIGHTS', 'Ce que la recherche suggere pour l\'experience produit', 'Les enseignements convergent vers une promesse simple : rendre une information complexe utile, fiable et actionnable.')

    insight_cards=[
        ('COMPRENDRE','Donner du sens aux variations et aux symptomes plutot que montrer uniquement des donnees.',SAGE),
        ('ANTICIPER','Aider l\'utilisatrice a reperer les periodes sensibles et a mieux organiser son quotidien.',LILAC),
        ('SIMPLIFIER','Transformer des indicateurs complexes en visualisations et messages faciles a interpreter.',IVORY),
        ('CREDIBILISER','Rassurer par la validation scientifique, la precision et la transparence sur les limites.',ROSE),
        ('PROTEGER','Faire de la confidentialite et de la securite des donnees un element visible de la proposition de valeur.',SAGE),
        ('ACCOMPAGNER','Aller au-dela du tracking avec des recommandations et un lien possible avec les professionnels de sante.',LILAC)]
    xs=[22,82,142]; ys=[146,84]
    idx=0
    for y in ys:
        for x in xs:
            h,b,fill=insight_cards[idx]; idx+=1
            section_card(c,x*mm,y*mm,50*mm,48*mm,h,b,fill=fill,accent=TEAL_DARK)

    rounded_rect(c,22*mm,42*mm,166*mm,24*mm,10,fill=TEAL_DARK)
    c.setFillColor(WHITE); c.setFont(FONT_B,10); c.drawString(28*mm,57*mm,'PROMESSE A RETENIR')
    c.setFont(FONT,9); c.drawString(28*mm,48*mm,'Rendre l\'equilibre hormonal visible, comprehensible et utile au quotidien.')
    footer(c,8)


def page_reco(c):
    title(c, '08 - RECOMMANDATIONS', 'Passer d\'un concept attractif a une proposition credible', 'Les recommandations visent a reduire le risque d\'adoption tout en preservant le potentiel d\'innovation.')

    recos=[
        ('01','Renforcer la preuve scientifique','Prioriser validation, precision des capteurs, cadre d\'usage et discours transparent.'),
        ('02','Simplifier l\'experience','Presenter des insights concrets, visuels et actionnables plutot qu\'un tableau de donnees brut.'),
        ('03','Construire la confiance','Rendre visibles la securite, la gestion du consentement et la protection des donnees.'),
        ('04','Clarifier le positionnement','Arbitrer entre bien-etre / prevention et dispositif medical certifie selon la strategie de lancement.'),
        ('05','Developper par etapes','Commencer avec une proposition focalisee, puis ouvrir progressivement aux professionnels de sante et a de nouvelles gammes.')]
    y=171*mm
    for n,h,b in recos:
        c.setFillColor(SAGE); c.circle(29*mm,y+2*mm,7*mm,fill=1,stroke=0)
        c.setFillColor(TEAL_DARK); c.setFont(FONT_B,8); c.drawCentredString(29*mm,y,n)
        c.setFillColor(INK); c.setFont(FONT_B,10.5); c.drawString(42*mm,y+3*mm,h)
        draw_text(c,b,42*mm,y-7*mm,140*mm,size=8.5,color=MUTED,leading=11)
        y -= 30*mm

    footer(c,9)


def page_close(c):
    c.setFillColor(TEAL_DARK); c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(SAGE); c.circle(W-26*mm,H-30*mm,25*mm,fill=1,stroke=0)
    c.setFillColor(LILAC); c.circle(12*mm,18*mm,20*mm,fill=1,stroke=0)
    c.setFillColor(WHITE); c.setFont(FONT_B,9); c.drawString(24*mm,H-36*mm,'09 - BILAN')
    c.setFont(FONT_B,28); c.drawString(24*mm,H-61*mm,'Analyser. Ecouter. Structurer.')
    c.setFont(FONT_B,28); c.drawString(24*mm,H-77*mm,'Recommander.')
    draw_text(c,'Ce projet m\'a permis de relier analyse documentaire, benchmark, recherche qualitative et reflexion strategique afin de transformer une idee d\'innovation en hypothese de marche structuree.',24*mm,H-97*mm,150*mm,size=11,color=WHITE,leading=15)

    rounded_rect(c,24*mm,82*mm,162*mm,62*mm,14,fill=WHITE)
    c.setFillColor(TEAL_DARK); c.setFont(FONT_B,10); c.drawString(34*mm,129*mm,'COMPETENCES RENFORCEES')
    skills=['Etude de marche','Benchmark concurrentiel','Recherche utilisateur','Analyse qualitative','Recommandations strategiques','Travail en equipe','Gestion de projet']
    x=34*mm; y=111*mm
    for s in skills:
        w=pill(c,x,y,s,fill=SAGE,color=TEAL_DARK)
        x += w+5
        if x > W-62*mm:
            x=34*mm; y -= 24

    c.setFillColor(WHITE); c.setFont(FONT_B,12); c.drawString(24*mm,47*mm,'Assa TRAORE')
    c.setFont(FONT,9); c.drawString(24*mm,39*mm,'Management de projet - Strategie - Marketing - Consulting')
    c.setFont(FONT_B,8); c.drawString(24*mm,29*mm,'GitHub : github.com/AssaT17')
    c.drawString(24*mm,23*mm,'LinkedIn : linkedin.com/in/assatraore')
    c.setFillColor(HexColor('#C8D8D6')); c.setFont(FONT,7); c.drawRightString(W-24*mm,18*mm,'Projet academique presente dans une version portfolio professionnelle.')


def build():
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle('HORMONA - Market Research & Innovation Strategy - Assa TRAORE')
    c.setAuthor('Assa TRAORE')
    pages=[page_cover,page_context,page_concept,page_market,page_strategy,page_benchmark,page_research,page_insights,page_reco,page_close]
    for fn in pages:
        fn(c); c.showPage()
    c.save()
    print(OUT)

if __name__ == '__main__':
    build()
