from MWC import MWC
import math
from datetime import datetime


syllables = [' ','a','â','ã','aê','ãe','ãen','ãens','ães','al','als','am','âm','ãm','an','ân','ãn','ans','âns','ãns','aô','âo','ão','aôn','ãos','ar','ars','as','ãs','ba','bâ','bã','bal','bals','bam','ban','bân','bão','bar','bars','bas','be','bê','bel','bêl','bels','bem','ben','bên','bens','ber','bêr','bers','bes','bês','bi','biâ','biã','biân','biê','biên','bil','bim','bin','bins','bir','bis','bla','blam','blan','blar','blas','ble','blem','blen','bler','bles','bli','blim','blin','blir','blis','blo','blon','blu','blum','blun','blus','bo','bô','bõ','boã','boê','bõe','boêm','bões','bol','bols','bom','bon','bôn','bons','bor','bors','bos','bôs','bra','brâ','brã','bral','bram','brâm','bran','brão','brar','bras','brãs','bre','brel','brem','bren','brer','bres','bri','briã','bril','brim','brin','briõ','brir','bris','bro','brô','brõ','brõe','brões','brol','brom','bron','brôn','bros','bru','brul','brum','brun','brus','bu','bul','bum','bun','buns','bur','bus','ca','câ','cã','ça','çã','cãe','cães','cal','çal','cam','câm','çam','can','cân','çan','cans','caô','cão','ção','caôn','çãos','car','çar','cars','cas','cãs','ças','çãs','ce','cê','çe','ceâ','ceân','cel','cels','cem','cêm','çem','cen','cên','cens','cer','cêr','ces','cês','cha','chã','chal','cham','chan','chão','chãos','char','chas','che','chê','chel','chem','chen','cher','ches','chês','chi','chil','chim','chin','chir','chis','cho','chô','chõ','chõe','chões','chol','chon','chor','chos','chu','chul','chum','chur','chus','ci','çi','ciã','ciãs','ciê','ciên','cil','cim','cin','çin','cir','cis','co','cô','cõ','ço','çô','çõ','cõe','çõe','cões','ções','col','çol','com','côm','çom','con','côn','çon','çôn','cons','côns','çons','cor','côr','çor','cors','cos','ços','cu','çu','cul','çul','cum','çum','cun','cuns','cur','çur','curs','cus','da','dâ','dã','dal','dam','dâm','dan','dân','dans','dão','dãos','dar','dars','das','dãs','de','dê','deã','del','dels','dem','dêm','den','dên','dens','deõ','der','dêr','ders','des','dês','di','diâ','diã','diâm','diãs','diê','diên','dil','dils','dim','din','dins','diô','diõ','diôn','dir','dis','do','dô','dõ','dõe','dões','dol','dom','dôm','don','dôn','dons','dor','dôr','dors','dos','dra','drã','dral','dram','dran','drão','drar','dras','dre','drel','drem','dren','dres','dri','dril','drim','drin','driõ','dris','dro','drô','drõ','drõe','drões','drol','drom','drôm','dron','drôn','dros','dru','drum','drus','du','dul','dum','dun','dur','durs','dus','e','ê','eâ','eã','eâm','eân','eãn','eãns','eãs','el','êl','els','em','êm','en','ên','ens','êns','eô','eõ','eôm','eôn','er','êr','ers','es','ês','fa','fâ','fã','fal','fals','fam','fâm','fan','fân','fão','fãos','far','fars','fas','fãs','fe','fê','fel','fem','fêm','fen','fên','fens','fer','fers','fes','fi','fil','fim','fin','fins','fir','firs','fis','fla','flâ','flam','flâm','flan','flar','flas','fle','flem','fler','fles','fli','flin','flo','flon','flor','flu','fluê','fluên','flum','fo','fô','fõ','fõe','fões','fol','fôl','fom','fon','fôn','fons','for','fôr','fors','fos','fôs','fra','frâ','frã','fral','fram','fran','frân','frans','frão','frar','fras','fre','frê','frem','frêm','fren','frên','frer','frêr','fres','frês','fri','frim','frin','fris','fro','frô','frõ','frõe','frões','from','fron','frôn','frons','fros','fru','frum','frun','frus','fu','ful','fum','fun','fur','fus','ga','gâ','gã','gal','gals','gam','gâm','gan','gân','gans','gão','gãos','gar','gas','gãs','ge','gê','gel','gels','gem','gêm','gen','gên','gens','geô','geôm','ger','gers','ges','gês','gi','giã','giê','giên','gil','gils','gim','gin','giõ','gir','gis','gla','glâ','glan','glân','glas','gle','glê','glen','gler','gles','glês','gli','glin','glis','glo','glom','glor','glos','glu','go','gô','gõ','gõe','gões','gol','gols','gom','gôm','gon','gôn','gons','gor','gos','gra','grâ','grã','gral','gram','gran','grân','grão','grãos','grar','gras','gre','grê','grel','grem','grêm','gren','grens','gres','gri','griã','gril','grim','grin','grir','gris','gro','grô','grol','gron','grôn','gror','gros','gru','gruê','gruên','grul','grum','grun','grur','gu','guã','guê','guês','gul','gum','gun','guns','gur','gus','i','iâ','iã','iâm','iân','iãs','iê','iên','il','ils','im','in','ins','iô','iõ','iôn','ir','irs','is','ja','jâ','jã','jal','jam','jâm','jan','jân','jans','jão','jar','jas','je','jel','jem','jen','jens','jer','jers','jes','ji','jil','jim','jin','jir','jis','jo','jô','jõ','joã','jõe','jões','jol','jom','jon','jôn','jor','jos','ju','jul','jum','jun','juns','jur','jus','ka','kal','kam','kan','kar','kas','ke','kê','kel','kels','kem','ken','kên','kens','ker','kes','ki','kil','kim','kin','kins','kir','kis','kla','klan','kle','kler','kli','klin','klo','klor','klors','ko','kol','kom','kon','kor','kos','kra','kran','kre','krem','kri','kris','kro','kru','ksa','kso','kson','ku','kun','kur','la','lâ','lã','lãe','lães','lal','lam','lâm','lan','lân','lans','lão','lar','lars','las','lãs','le','lê','leã','leãn','leãns','lel','lem','lêm','len','lên','lens','leô','leõ','leôn','ler','lêr','lers','les','lês','li','liã','liê','liên','lil','lim','lin','lins','liô','liõ','liôn','lir','lis','lo','lô','lõ','lõe','lões','lol','lom','lôm','lon','lôn','lons','lor','lors','los','lôs','lu','luê','luên','lul','lum','lun','lur','lus','ma','mâ','mã','mãe','mães','mal','mals','mam','mãm','man','mân','mans','mão','mãos','mar','mars','mas','mãs','me','mê','meã','mel','mem','mêm','men','mên','mens','mer','mêr','mers','mes','mês','mi','miã','mil','mim','min','mins','mir','mis','mo','mô','mõ','mõe','mões','mol','mom','môm','mon','môn','mons','mor','mors','mos','mu','mul','muls','mum','mun','muns','mur','mus','na','nâ','nã','nal','nam','nâm','nan','nân','não','nar','nas','ne','nê','nel','nels','nem','nêm','nen','nên','nens','ner','ners','nes','nês','nha','nhã','nhal','nham','nhan','nhão','nhar','nhas','nhãs','nhe','nhê','nhel','nhem','nhen','nhens','nher','nhes','nhês','nhi','nhin','nhir','nhis','nho','nhô','nhõ','nhõe','nhões','nhol','nhon','nhor','nhos','nhu','nhum','ni','niã','niê','niên','nil','nils','nim','nin','nins','niõ','nir','nirs','nis','no','nô','nõ','noê','nõe','noêm','nões','nol','nom','nôm','non','nôn','nor','nos','nu','nuê','nuên','nul','num','nun','nuns','nur','nus','o','ô','õ','oã','oê','õe','oêm','õem','ões','ol','ôl','ols','om','ôm','on','ôn','ons','ôns','or','ôr','ors','os','ôs','pa','pâ','pã','pãe','pãen','pãens','pães','pal','pam','pan','pân','pans','pão','par','pars','pas','pe','pê','peã','peãs','pel','pêl','pem','pen','pên','pens','peõ','per','pêr','pers','pes','pês','pi','piã','piê','piên','pil','pim','pin','pins','piõ','pir','pis','pla','plâ','plam','plan','plar','plas','ple','plê','plem','plen','plên','pler','ples','pli','plim','plin','plis','plo','plom','plon','plor','plos','plu','plum','plur','plus','po','pô','põ','põe','põem','pões','pol','pom','pon','pôn','pons','por','pôr','pos','pôs','pra','pral','pram','pran','prar','pras','pre','prê','preâ','preâm','prel','prem','prêm','pren','prens','prer','pres','pri','prim','prin','prir','pris','pro','prô','proê','proêm','prol','prom','pron','prôn','pror','pros','pru','prum','prur','prus','pu','puã','pul','puls','pum','pun','pur','pus','qua','que','qui','quo','ra','râ','rã','raê','rãe','rães','ral','ram','râm','ran','rân','rans','râns','raô','rão','raôn','rãos','rar','ras','rãs','re','rê','reâ','reã','reâm','rel','rêl','rem','rêm','ren','rên','rens','reô','reõ','reôn','rer','rêr','res','rês','ri','riâ','riã','riân','riê','riên','ril','rim','rin','rins','riô','riõ','riôn','rir','ris','ro','rô','rõ','roê','rõe','roêm','rões','rol','rom','rôm','ron','rôn','rons','ror','ros','rôs','ru','ruã','ruê','ruên','rul','rum','run','runs','ruõ','rur','rus','sa','sâ','sã','sal','sals','sam','sâm','san','sân','sãn','sans','sâns','saô','sâo','são','saôn','sãos','sar','sas','sãs','se','sê','sel','sem','sêm','sen','sên','sens','ser','ses','si','siâ','siã','siân','siê','sil','sim','sin','sins','siõ','sir','sis','so','sô','sõ','sõe','sões','sol','sôl','sols','som','sôm','son','sôn','sons','sor','sôr','sos','sôs','su','sul','suls','sum','sun','sur','surs','sus','ta','tâ','tã','tãe','tães','tal','tam','tâm','tãm','tan','tân','tão','tãos','tar','tars','tas','tãs','te','tê','teã','tel','tem','têm','ten','tên','tens','têns','ter','têr','ters','tes','tês','ti','tiã','til','tim','tin','tins','tiõ','tir','tirs','tis','tla','tlâ','tlan','tlân','tle','tlem','tler','tles','tli','tlin','to','tô','tõ','tõe','tões','tol','tols','tom','tôm','ton','tôn','tons','tor','tôr','tors','tos','tra','trâ','trã','tral','tram','trâm','tran','trân','trans','trâns','trão','trar','tras','tre','trê','trel','trêl','trem','trêm','tren','trên','trens','tres','três','tri','triâ','triã','triân','triê','triên','tril','trim','trin','trins','triô','triõ','triôn','trir','tris','tro','trô','trõ','trõe','trões','trol','trom','tron','trôn','trons','tror','tros','tru','truã','trul','trum','trun','truõ','trus','tu','tul','tum','tun','tur','tus','u','uâ','uã','uân','uê','uên','uês','ul','uls','um','un','uns','uõ','ur','urs','us','va','vâ','vã','vãe','vães','val','vals','vam','van','vân','vão','vãos','var','vas','vãs','ve','vê','vel','vels','vem','vêm','ven','vên','vens','ver','vêr','vers','ves','vês','vi','viâ','viã','viân','viê','viên','vil','vils','vim','vin','viõ','vir','vis','vo','vô','võ','võe','vões','vol','vôl','vols','vom','vôm','von','vôn','vor','vos','vôs','vra','vrã','vral','vram','vran','vrão','vrar','vras','vre','vrem','vren','vrens','vres','vri','vrin','vro','vrõ','vrõe','vrões','vrol','vros','vu','vul','vuls','vum','vur','xa','xâ','xã','xal','xam','xan','xân','xão','xar','xas','xe','xê','xel','xem','xen','xên','xer','xes','xi','xil','xim','xin','xins','xir','xis','xo','xô','xõ','xõe','xões','xol','xon','xôn','xor','xos','xu','xul','xum','xun','xur','xus','za','zâ','zã','zal','zam','zan','zân','zans','zão','zar','zas','ze','zê','zel','zem','zêm','zen','zên','zer','zers','zes','zi','ziâ','ziân','zil','zils','zim','zin','zir','zis','zo','zô','zõ','zõe','zões','zol','zom','zon','zôn','zons','zor','zos','zu','zuê','zuês','zul','zum','zun','zur']

class RandomSyllabes:

    def extract_date_parts(self, timestamp):
        # Separar o timestamp em segundos e milissegundos
        seconds, millis = divmod(int(timestamp), 1000)

        # Criar um objeto datetime a partir dos segundos
        dt_object = datetime.fromtimestamp(seconds)

        # Extrair as partes e colocá-las em uma lista
        date_parts = [
            dt_object.year,
            dt_object.month,
            dt_object.day,
            dt_object.hour,
            dt_object.minute,
            dt_object.second,
            millis
        ]

        return date_parts

    def get_random_syllables(self,seed, start, end):

        # Inicializa o gerador de números aleatórios com a semente dada
        mwc_gen = MWC(seed, 123321)

        # Gera uma lista aleatória de sílabas
        random_syllables = []
        for i in range(start, end):
            num = mwc_gen.random_normalized()
            index = math.floor(num*(len(syllables)-1) )
            random_syllables.append(syllables[index])

        return random_syllables

    def get_random_syllables2(self,seed1, seed2,start, end):

        # Inicializa o gerador de números aleatórios com a semente dada
        mwc_gen = MWC(seed1, seed2)

        # Gera uma lista aleatória de sílabas
        random_syllables = []
        for i in range(start, end):
            num = mwc_gen.random_normalized()
            index = math.floor(num*(len(syllables)-1) )
            random_syllables.append(syllables[index])

        return random_syllables

    def generate(self,list,timestampList,min_percent_over_threshold):
        textList = []
        for item in list:
            sil = self.get_random_syllables2(item[2], item[4], 0, 3)
            print(''.join(sil))
            textList.append(''.join(sil))

        return textList

    def generate2(self,list,timestampList,min_percent_over_threshold):
        for item in list:
            sil = self.get_random_syllables(item[2], 0,
                                               self.extract_date_parts(timestampList[item[2]])[5])
            print(''.join(sil))



# mwc_gen = MWC(seed1=12345, seed2=67890)
#
# # Gera um número pseudoaleatório não normalizado (inteiro)
# # print(mwc_gen.random())
#
# teste = RandomSyllabes();
# result = teste.get_random_syllables(123.543543534534534,0,5)
# print('Resultado',result)