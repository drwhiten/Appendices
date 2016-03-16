#pragma rtGlobals=1

// To be used after load_() and Threshold_() in Appendix III
Function size()
	variable mon_bright=15
	wave thresholded_donor_events, thresholded_acceptor_events
	variable a,b,c,d,e,f,g,sizevar,ca=-4
	make/o/n=50 scalex,scaley

	for(a=0;a<50;a+=1)
		scalex[a]=b/mon_bright
		scaley[a]=ca
		b+=10
		ca+=0.15
	endfor

	make/o/n=(50,50) size_matrix=0

	for(sizevar=10;(sizevar<500);sizevar+=10)
		make/o/n=1 ratio,temp
		b=0
		for(a=0;a<(dimsize(thresholded_donor_events,0));a+=1)
			if(thresholded_donor_events[a]<(sizevar)&&thresholded_donor_events[a]>(sizevar-10))
				redimension/n=(b+1) temp
				temp[b]=ln(thresholded_acceptor_events[a]/thresholded_donor_events[a])
				b+=1
			endif
		endfor
		Make/N=50/O temp_Hist;DelayUpdate
		Histogram/B={-4,0.15,50} temp,temp_Hist

		for(g=0;g<50;g+=1)
			if(temp_hist[g]==0)
				size_matrix[e][g]=0
			else
				size_matrix[e][g]=ln(temp_hist[g])
			endif
		endfor
		e+=1
	endfor

	Display;AppendMatrixContour size_matrix vs {scalex,scaley}
	ModifyContour size_matrix labels=0,autoLevels={*,*,100}
	Label left "ln(red/blue)";DelayUpdate
	Label bottom "A-beta monomers"
	ColorScale/C/N=text0/F=0/A=RC/X=0.00/Y=0.00/E contour=size_matrix;DelayUpdate
	ColorScale/C/N=text0 "ln(no. of oligomers)"
	ModifyGraph swapXY=1
end
