if [ $# -eq 1 ]; then
searchfile="./"$1
outputfile="./summary_"$1
else
nowepoch=`date +%s`
let yestepoch=$nowepoch-24*60*60
yesterday=`date -d @$yestepoch +%Y%m%d`
searchfile=`echo "./proxyall_"$yesterday".csv"`
outputfile=`echo "./summary_proxyall_"$yesterday".csv"`
fi
let totalrequests=0
let peakrequests=0
let countgood=0
let countwarning=0
let countcritical=0
let criticalthreshold=999
let warningthreshold=799
let linenumber=0
while read -r line; do
if [ "$linenumber" -gt 0 ]; then
requests=`echo "$line" | cut -d',' -f4`
let totalrequests=$totalrequests+$requests
if [ "$requests" -gt "$peakrequests" ]; then
let peakrequests=$requests
fi
feconnections=`echo "$line" | cut -d',' -f6`
if [ "$feconnections" -gt "$criticalthreshold" ]; then
let countcritical=$countcritical+1
else
if [ "$feconnections" -gt "$warningthreshold" ]; then
let countwarning=$countwarning+1
else
let countgood=$countgood+1
fi
fi
fi
let linenumber=$linenumber+1
done < $searchfile
echo "totalrequests,peakrequests,goodminutes,warningminutes,criticalminutes" > $outputfile
echo "$totalrequests,$peakrequests,$countgood,$countwarning,$countcritical" >> $outputfile

