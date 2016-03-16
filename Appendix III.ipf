#pragma rtGlobals=1

function Load_()
	String doprompttitle="Details of files to load"
	string foldername=""
	string filename="asyn"
	variable first=0 
	variable last=79
	variable Auto_blue=0
	variable Auto_red=0
	variable crosst=0
	
	prompt foldername, "Folder name: "		
	prompt filename "File name (no suffix): "
	prompt first, "First filenumber: "
	prompt last, "Last filenumber: "
	prompt auto_blue, "Autofluorescence in channel A: "
	prompt auto_red, "Autofluorescence in channel B: "
	prompt crosst, "Crosstalk: "								
	doprompt doprompttitle, foldername,filename,first,last,auto_blue,auto_red,crosst								
	variable c
	setdatafolder root:
	newdatafolder/s $foldername
	make/o/n=1 unthresholded_donor_events,unthresholded_acceptor_events  

	newpath/Q path1
	pathinfo path1
	
	string path=S_path
	string pathway=path+filename
	string num
					
	for(c=first;c<=last;c+=1)
		if(c<10)
			num="000"+num2str(c)
		elseif(c<100)
			num="00"+num2str(c)
		elseif(c<1000)
			num="0"+num2str(c)
		endif
												
		string loader=pathway+num+".dat"				
		GBLoadWave/Q/V/T={32,4}/W=2 loader
		wave wave0,wave1
												
		variable e,k									
		for(e=0;e<=(Numpnts(wave0));e+=1)
			redimension/N=(k+1) unthresholded_donor_events,unthresholded_acceptor_events
			unthresholded_donor_events[k]=wave0[e]-auto_blue			
			unthresholded_acceptor_events [k]=wave1[e]-auto_red-crosst*wave0[e]
			k+=1	
		endfor
		
		killwaves wave0	
		killwaves wave1
		
		Print "Opening file #",num
	endfor
	
Print "Files opened."	
end

function Threshold_()		
	variable donor=10
	variable Acceptor=10
	prompt donor, "Donor: "
	prompt acceptor, "Acceptor: "
	string doprompttitle="Thresholds to use"
	doprompt doprompttitle, donor, acceptor	
	
	wave unthresholded_donor_events,unthresholded_acceptor_events
	
	variable coinc=0,Arate=0,Brate=0,e	
	make/o/N=1 thresholded_donor_events,thresholded_acceptor_events,donor_desynch,acceptor_desynch,zplot,z_desynch
	for(e=0;e<(dimsize(unthresholded_donor_events,0));e+=1)
		if((unthresholded_donor_events[e])>donor && (unthresholded_acceptor_events[e])>acceptor)
			redimension/N=(coinc+1) thresholded_donor_events,thresholded_acceptor_events,zplot
			thresholded_donor_events[coinc]=unthresholded_donor_events[e]
			thresholded_acceptor_events[coinc]=unthresholded_acceptor_events[e]
			zplot[coinc]=ln(thresholded_acceptor_events[coinc]/thresholded_donor_events[coinc])
			coinc+=1
		endif
		
		if((unthresholded_donor_events[e])>donor)
			Arate+=1
		Endif

		if((unthresholded_acceptor_events[e])>acceptor)
			Brate+=1
		endif
	endfor

	variable d												
	for(e=0;e<(dimsize(unthresholded_donor_events,0));e+=1)
		variable num2=round(enoise(dimsize(unthresholded_donor_events,0)))
		if(num2<0)
			num2=-1*num2
		endif
		if((unthresholded_donor_events[e])>donor && (unthresholded_acceptor_events[num2])>acceptor)
			redimension/N=(d+1) donor_desynch,acceptor_desynch,z_desynch
			donor_desynch[d]=unthresholded_donor_events[e]
			acceptor_desynch[d]=unthresholded_acceptor_events[num2]
			z_desynch[d]=ln(acceptor_desynch[d]/donor_desynch[d])

			d+=1
		endif
	endfor
	make/o/n=1 coincident=coinc,donorrate=arate,acceptorrate=brate,desynchrate=d,QValue
	variable q=(coinc-d)/(arate+brate-(coinc-d)) 	

	QValue[0]=q	
	string q_val=num2str(q)
	Make/N=30/O zplot_Hist,zdesynch_hist;DelayUpdate
	Histogram/B={-3,0.2,30} zplot,zplot_Hist
	Histogram/B={-3,0.2,30} z_desynch,zdesynch_Hist
Print "Data thresholded."
end	

function MaxQ_matrix_func_()	
	variable threshold=0
	prompt threshold, "Threshold: "
	string doprompttitle = "Threshold limit"
	doprompt doprompttitle,threshold
	
	variable donorthreshold=threshold,acceptorthreshol=threshold
	wave unthresholded_donor_events,unthresholded_acceptor_events
	variable line=0,donorcycler																		
	variable acceptorthreshold=(acceptorthreshol+1)		
	for(donorcycler=0;donorcycler<=donorthreshold;donorcycler+=1)	
		make/o/n=(acceptorthreshold) pretendQwave	
		make/o/n=(acceptorthreshold) pretenddesynchwave
		make/o/n=(acceptorthreshold) pretendrealwave
		make/o/n=(acceptorthreshold) pretendrealminusdwave
	
		variable acceptorcycler
		make/o/n=1 q_donorthreshold
		make/o/n=1 realrate_donorthreshold
		make/o/n=1 realminusd_donorthreshold
		make/o/n=1 desynchrate_donorthreshold
	
		for(acceptorcycler=0;acceptorcycler<=(acceptorthreshold);acceptorcycler+=1)		
			variable h=0,coinc=0,d=0,Arate=0,Brate=0
			make/o/N=1 TEMP_donor_events,TEMP_acceptor_events							
			make/o/N=1 donor_desynch,acceptor_desynch
		
			for(h=0;h<(Numpnts(unthresholded_donor_events));h+=1)		
				if((unthresholded_donor_events[h])>donorcycler && (unthresholded_acceptor_events[h])>acceptorcycler)
					redimension/N=(coinc+1) TEMP_donor_events,TEMP_acceptor_events											
					TEMP_donor_events[coinc]=unthresholded_donor_events[h]																
					TEMP_acceptor_events[coinc]=unthresholded_acceptor_events[h]
					coinc+=1						
				endif
			
				variable random=round(enoise(Numpnts(unthresholded_donor_events)))												
				if(random<0)
					random=-1*random
				endif
			
				if((unthresholded_donor_events[h])>donorcycler && (unthresholded_acceptor_events[random])>acceptorcycler)
					redimension/N=(d+1) donor_desynch,acceptor_desynch
					donor_desynch[d]=unthresholded_donor_events[h]
					acceptor_desynch[d]=unthresholded_acceptor_events[random]
					d+=1											
				endif
			
				if((unthresholded_donor_events[h])>donorcycler)		
					Arate+=1
				endif
		
				if((unthresholded_acceptor_events[h])>acceptorcycler)		
					Brate+=1
				endif
		
			endfor
												
			variable qis=(coinc-d)/(arate+brate-(coinc-d))		
			pretendQwave[acceptorcycler]=qis				
			pretenddesynchwave[acceptorcycler]=d
			pretendrealwave[acceptorcycler]=coinc	
			pretendrealminusdwave[acceptorcycler]=coinc-d
										
			duplicate/o pretendQwave $(nameOfWave(q_donorthreshold)+num2str(donorcycler))
			duplicate/o pretenddesynchwave $(nameOfWave(desynchrate_donorthreshold)+num2str(donorcycler))
			duplicate/o pretendrealwave $(nameOfWave(realrate_donorthreshold)+num2str(donorcycler))
			duplicate/o pretendrealminusdwave $(nameOfWave(realminusd_donorthreshold)+num2str(donorcycler))
	
		endfor
	
		killwaves desynchrate_donorthreshold	
		killwaves q_donorthreshold	
		killwaves realrate_donorthreshold
		killwaves realminusd_donorthreshold
		killwaves acceptor_desynch
		killwaves donor_desynch

	endfor

	Concatenate/o/KILL WaveList("q_donorthreshold*", ";", ""), q_matrix	
	Concatenate/o/KILL WaveList("desynchrate_donorthreshold*", ";", ""), desynch_matrix
	Concatenate/o/KILL WaveList("realrate_donorthreshold*", ";", ""), realrate_matrix
	Concatenate/o/KILL WaveList("realminusd_donorthreshold*", ";", ""), realminusd_matrix

	Display as "Q-Value";AppendImage q_matrix	
	Label left "Donor threshold";DelayUpdate
	Label bottom "Acceptor threshold"
	ModifyImage q_matrix ctab= {*,*,Rainbow256,0}
	ColorScale/C/N=text0/F=0/A=RC/E contour=ln_FRET_Matrix_1Bin_Mass
	ColorScale/C/N=text0  ctab={0,100,Rainbow,0}

	Display as "Desynch events";AppendImage desynch_matrix
	Label left "Donor threshold";DelayUpdate
	Label bottom "Acceptor threshold"
	ModifyImage desynch_matrix ctab= {*,*,Rainbow256,0}
	ColorScale/C/N=text0/F=0/A=RC/E contour=ln_FRET_Matrix_1Bin_Mass
	ColorScale/C/N=text0  ctab={0,100,Rainbow,0}

	Display as "Coincident events";AppendImage realrate_matrix
	Label left "Donor threshold";DelayUpdate
	Label bottom "Acceptor threshold"
	ModifyImage realrate_matrix ctab= {*,*,Rainbow256,0}
	ColorScale/C/N=text0/F=0/A=RC/E contour=ln_FRET_Matrix_1Bin_Mass
	ColorScale/C/N=text0  ctab={0,100,Rainbow,0}

	Display as "Coincident - chance events";AppendImage realminusd_matrix
	Label left "Donor threshold";DelayUpdate
	Label bottom "Acceptor threshold"
	ModifyImage realminusd_matrix ctab= {*,*,Rainbow256,0}
	ColorScale/C/N=text0/F=0/A=RC/E contour=ln_FRET_Matrix_1Bin_Mass
	ColorScale/C/N=text0  ctab={0,100,Rainbow,0}
	Print "Calculations complete."
end