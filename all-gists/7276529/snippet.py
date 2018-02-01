J=1;exec'''z="";b=-1.6;exec'
x=y=0;exec"x,y=2*x*y+J,y*y-x
*x+b;"*20;z+=" O"[x*x+y*y<2]
;b+=.040;'*60;print z;J-=.10
;'''.replace('\n','')*20#Jay
