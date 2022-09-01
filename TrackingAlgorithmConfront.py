import cv2
import wx
import os

video_list =[]
files = os. listdir(os.getcwd())
for file in files:
    if file.__contains__("mp4"):
       video_list.append(file)
print(video_list)

app = wx.App(False)
width, height = wx.GetDisplaySize()
print(video_list)
# aereoplani , car_racing , mucche , pingpong ,soccer, tennis , pingpong_Trim
nome_video ="road_Trim.mp4" #"pingpong.mp4"#"soccer.mp4"#video_list[7]#input("Video index:")
tracker_types = ['BOOSTING','KCF','MIL', 'TLD','MOSSE','MEDIANFLOW', 'CSRT']  #'BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW',  'MOSSE', 'CSRT']
null = "0/0/0/0"

file = open('Track_coord_'+nome_video[:-4] +'.txt', 'w')
bbox_init = False
file.writelines('\n'+"TYPE /NFRAME / FPS/ A_X /A_Y / B_X /B_Y")
for tracker_type in tracker_types:
    if tracker_type == 'BOOSTING':
        tracker = cv2.legacy.TrackerBoosting_create()
    if tracker_type == 'MIL':
        tracker = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    if tracker_type == 'TLD':
        tracker = cv2.legacy.TrackerTLD_create()
    if tracker_type == 'MEDIANFLOW':
        tracker = cv2.legacy.TrackerMedianFlow_create()
    if tracker_type == 'MOSSE':
        tracker = cv2.legacy.TrackerMOSSE_create()
    if tracker_type == "CSRT":
        tracker = cv2.TrackerCSRT_create()

    # Leggo il video
    print("Leeggo")
    video = cv2.VideoCapture(nome_video)
    ret, frame = video.read()

    # Aggiusto il video per farlo entrare nello schermo (dipende dalla qualità del file)
    if ret:
        print("LETTO")
    frame_height, frame_width = frame.shape[:2]
    if frame_width > width | frame_height > height:
        frame_width = frame_width//2
        frame_height = frame_height//2
    frame = cv2.resize(frame, [frame_width, frame_height])

    # Preparo il file da scrivere
    output = cv2.VideoWriter(nome_video[:-4]+"_"+tracker_type+'.avi', cv2.VideoWriter_fourcc(*'XVID'), 60.0,(frame_width, frame_height), True)
    if not ret:
        print('cannot read the video')

    # Seleziono l'oggetto da tracciare
    if bbox_init == False:
        print("Selezionare obj da tracciare")
        bbox_start = cv2.selectROI("select the object to track",frame, False)
        bbox_init = True

    # Inizializzo il tracker
    bbox = bbox_start
    print(bbox)
    print(bbox_start)
    ret = tracker.init(frame, bbox)
    n_frame=0

    # Inizio a tracciare e salvo le coordinate nel file:
    while True:
        ret, frame = video.read()
        if not ret:
            print('something went wrong')
            break

        frame = cv2.resize(frame, [frame_width , frame_height ])
        timer = cv2.getTickCount()
        ret, bbox = tracker.update(frame)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
        n_frame = n_frame +1

        if ret:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            print(p1 + p2)
            line= "\n "+tracker_type+"/ "+str(n_frame) +"/ " + str(int(fps))+ "/ " +str(int(bbox[0]))+"/ "+str(int(bbox[1]))+"/ "+str(int(bbox[0] + bbox[2]))+"/"+ str(int(bbox[1] + bbox[3]))
            file.writelines(line)
        else:
            cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
            line = "\n " +tracker_type+"/ "+str(n_frame) + "/ " + str(int(fps)) + "/ " + str(null)
            file.writelines(line)

        cv2.putText(frame, tracker_type + " Tracker", (100, 20),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
        cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
        cv2.imshow("Tracking", frame)


        output.write(frame)
        k = cv2.waitKey(1) & 0xff
        if k == 27: break

    video.release()
    output.release()
cv2.destroyAllWindows()
file.close()


