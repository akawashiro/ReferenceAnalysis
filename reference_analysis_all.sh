#! /bin/bash

IFS=$'\n'
for q in `cat list_of_query | grep -v "#" `;do
    db=result/`echo $q | tr -d [:space:]`_one_sentence_filter.sqlite3
    if [ -e $db ];then
        echo $db exists. This query is passed.
    else
        echo $db does not exists.
        
        echo get_event_info.py &&
        ( time python get_event_info.py $db "$q") 2>&1 | tee -a reference_analysis_all.log &&
        echo collect_article.py &&
        ( time python collect_article.py $db --include-neighbor 0 --use-all 1 ) 2>&1 | tee -a reference_analysis_all.log &&
        echo extract_word.py &&
        ( time python extract_word.py $db --no_heidel ) 2>&1 | tee -a reference_analysis_all.log &&
        echo calc_word_val.py &&
        ( time python calc_word_val.py $db ) 2>&1 | tee -a reference_analysis_all.log &&
        echo calc_word_score.py &&
        ( time python calc_word_score.py $db )  2>&1 | tee -a reference_analysis_all.log &&
        echo calc_ref_score.py &&
        ( time python calc_ref_score.py $db ) 2>&1 | tee -a reference_analysis_all.log
        # time python export_xlsx.py $db 2>&1 | tee -a reference_analysis_all.log
    fi

    db=result/`echo $q | tr -d [:space:]`_no_filter.sqlite3
    if [ -e $db ];then
        echo $db exists. This query is passed.
    else
        echo $db does not exists.

        echo get_event_info.py &&
        ( time python get_event_info.py $db "$q" ) 2>&1 | tee -a reference_analysis_all.log &&
        echo collect_article.py &&
        ( time python collect_article.py $db --include-neighbor 1000 --use-all 1 ) 2>&1 | tee -a reference_analysis_all.log &&
        echo extract_word.py &&
        ( time python extract_word.py $db --no_heidel ) 2>&1 | tee -a reference_analysis_all.log &&
        echo calc_word_val.py &&
        ( time python calc_word_val.py $db ) 2>&1 | tee -a reference_analysis_all.log &&
        echo calc_word_score.py &&
        ( time python calc_word_score.py $db )  2>&1 | tee -a reference_analysis_all.log &&
        echo calc_ref_score.py &&
        ( time python calc_ref_score.py $db ) 2>&1 | tee -a reference_analysis_all.log
        # time python export_xlsx.py $db 2>&1 | tee -a reference_analysis_all.log
    fi

done
