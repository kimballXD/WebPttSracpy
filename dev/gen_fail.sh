cat log.txt | grep "Spider error processing" | awk '{gsub(">","",$9);print $9}' > failed.txt
grep "Error processing" | awk '{gsub("[\047\054]","",$8); printf "https://www.ptt.cc/bbs/Gossiping/%s.html\n", $8}' >> failed.txt

