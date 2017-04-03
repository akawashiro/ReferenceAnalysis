reference_analysis

How to use this software?
1. Prepare list_of_query file.   
This file is a list event which you want to process.  
I prepare default list_of_query. Please change it as you like.  
You should adopt events which appear in New York Times database and have articles in wikipedia.

2. Prepare black list words in black_words_list directory.  
This is optional process. You can skip this process. If you want to set some black words for some queries, you can set it by this process. Please look files in black_words_list.

2. Run reference_analysis_all.sh  
This shell script run many python scripts and store the results under "result" directory. This script use sqlite3 and access to the New York Times database and CoreNLP.  
Please keep in mind that some query take very long time to process. When you don't have enough time you should skip that query. You can skip a query by stopping reference_analysis_all.sh and removing the query from list_of_query. This script cache calculated data to the database so you can feel free to stop this script by C-c.

3. Prepare list_of_sqlite3 file.  
This file is a list of sqlite3 databases which you want to process in the next step. I use following oneliner to make this file.  
ls -al result | sort -k 5 | awk '{print $9}' | sed -e "s:^:result/:g" | grep "sqlite3$" > list_of_sqlite3  
You mustn't sort by sort and awk. But sorting this file by database file is useful to make handy result quickly.

4. Run python sqlite3_to_pickle.py -ld list_of_sqlite3  
This python script calculates tf-idf value for each words in databases and store the caclulated results to "name-of-database .pickle" in result directory.

5. Run python summary_from_pickle.py -ld list_of_want_to_saummarize_sqlite3
This is last process to make summary xlsx file. You pick up some sqlite3 and write them to list_of_want_to_saummarize_sqlite3. Result is saved to summary_for_list_of_want_to_saummarize_sqlite3.xlsx.

Dependings  
- sqlite3
- New York Times database  
 You should have free access to http://lab.dl.kuis.kyoto-u.ac.jp/~adam/solr/select.
- CoreNLP  
You can download from http://nlp.stanford.edu/software/stanford-corenlp-full-2015-04-20.zip.  
Unzip it and rewrite CORENLPDIRECTORY in kawata_corenlp.py.
