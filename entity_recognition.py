import jsonimport spacy
# 1 INITIALIZING SPACY
nlp = spacy.load("en_core_web_sm")
# 2 MAPPING ALL ENTITY TYPE
entity_categories = {'e_1': 'Units', 'e_2': 'Magnitude', 'e_3': 'Definition', 'e_4': 'Variable', 'e_5': 'O', 'e_10': 'Equation'}def pool_builder_entity(chapter):    
# 3 LOADING FILE PATHS    
#chapter = 'Chapter 2'    
text_file = open('DataSet/' + chapter + '_Text.txt', encoding='utf-8')    
json_file = open('DataSet/' + chapter + '_JSON.json', encoding='utf-8')    
# 4 EXTRACTING TEXT FILE CONTENTS    
tfile_content = [line for line in text_file if line != "\n"]  
# list of sentences   
 tfile_content = [line.replace("\n", "  ") for line in tfile_content]    
 full_text = "".join(tfile_content)    
 len_each_sentence = [0] + [len(item) for item in tfile_content]    
 sentence_start_indexes = [len_each_sentence[0]]    
 for i in range(1, len(len_each_sentence)):        
    sentence_start_indexes.append(sentence_start_indexes[-1] + len_each_sentence[i])    
    sentence_idx_range = []  
    # index ranges of each sentence    
    for i in range(1, len(sentence_start_indexes)):        
        sentence_idx_range.append((sentence_start_indexes[i - 1], sentence_start_indexes[i]))    
        sentence_start_indexes = sentence_start_indexes[:-1]  
        # truncates this list    
        # 5 EXTRACTING JSON FILE CONTENTS    
        jfile_content = json.load(json_file)    
        entity_data = jfile_content['entities']    
        entity_index_tags = [{'text': data['offsets'][0]['text'], 'start': data['offsets'][0]['start'],                          
        'end': data['offsets'][0]['start'] + len(data['offsets'][0]['text']),                          
        'tag': entity_categories[data['classId']]} for data in entity_data]    
        # 6 DELETING TO SAVE MEMORY   
         del len_each_sentence    
         del entity_data    
         """ IDENTIFY THE ENTITIES THAT ARE IN BETWEEN A LONGER ENTITY E.G. VARIABLE IN A DEFINITION THE ENTITY_INDEX_TAGS IS THE ENTIRETY OF THE ANNOTATED ENTITIES. WE COMPARE EACH ENTITY (HEREIN AS ITEM) TO EACH OF THE ANNOTATED ENTITY TO CHECK IF IT IS PART OF A LONGER ENTITY """    
         part_of = []    
         encompassing = []    
         encompassing_index = []    
         for item in entity_index_tags:        
            i = 0        
            while i <= len(entity_index_tags) - 1:            
                # shorter entity is in between the longer entity            
                if entity_index_tags[i]['start'] < item['start'] and item['end'] < entity_index_tags[i]['end']:                
                    part_of.append(item)                
                    if {'index': i, 'item': entity_index_tags[i]} not in encompassing:                    
                        encompassing.append({'index': i, 'item': entity_index_tags[i]})                    
                        encompassing_index.append(i)            
                        # shorter entity is at the start of the longer entity            
                        if entity_index_tags[i]['start'] == item['start'] and item['end'] < entity_index_tags[i]['end']:                
                            part_of.append(item)                
                            if {'index': i, 'item': entity_index_tags[i]} not in encompassing:                    
                                encompassing.append({'index': i, 'item': entity_index_tags[i]})                    
                                encompassing_index.append(i)           
                                 # shorter entity is at the end of the longer entity            
                                 if entity_index_tags[i]['start'] < item['start'] and item['end'] == entity_index_tags[i]['end']:                
                                   part_of.append(item)                
                                   if {'index': i, 'item': entity_index_tags[i]} not in encompassing:                    
                                    encompassing.append({'index': i, 'item': entity_index_tags[i]})                    
                                    encompassing_index.append(i)            
                                    i = i + 1    
                                    encompassing_index.reverse()    
                                    for item in encompassing_index:        
                                        entity_index_tags.remove(entity_index_tags[item])    
                                        # dividing the annotated entities per sentence    
                                        grouped_entity_index_tags = [        [entity for entity in entity_index_tags if range[0] <= entity['start'] and entity['end'] <= range[1]] for range        in sentence_idx_range]   
                                        # removing the sentences with no entities    
                                        no_entt = []    
                                        for i in range(len(grouped_entity_index_tags)):        
                                            if grouped_entity_index_tags[i] == []:            
                                                no_entt.append(i)    
                                                no_entt.reverse()    
                                                for item in no_entt:        sentence_idx_range.pop(item)        tfile_content.pop(item)        sentence_start_indexes.pop(item)    grouped_entity_index_tags = [item for item in grouped_entity_index_tags if item != []]    gr_entity_index_tags = grouped_entity_index_tags    
                                                # filling the O's in between entities    
                                                """ WE START WITH FILLING THE O'S AT THE START AND END """    
                                                for i in range(len(grouped_entity_index_tags)):        
                                                    group = grouped_entity_index_tags[i]        
                                                    start_indexes = sentence_start_indexes[i]       
                                                    sentence_range = sentence_idx_range[i]        
                                                    if group[0]['start'] != start_indexes:            
                                                       group.insert(0, {                'text': full_text[sentence_range[0]: group[0]['start']],                'start': start_indexes, 'end': group[0]['start'], 'tag': 'O'})        if group[-1]['end'] != sentence_range[1]:            group.append({                'text': full_text[group[-1]['end']: sentence_range[1]],                'start': group[-1]['end'], 'end': sentence_range[1], 'tag': 'O'})    allgr_filled = []    for grouping in grouped_entity_index_tags:        grouped_filled = []        for i in range(1, len(grouping)):            if grouping[i - 1]['end'] == grouping[i]['start']:                grouped_filled.append(grouping[i - 1])                # print(grouping[i - 1])                # print(grouping[i])            else:                grouped_filled.append(grouping[i - 1])                grouped_filled.extend([{'text': full_text[grouping[i - 1]['end']: grouping[i]['start']],                                        'start': grouping[i - 1]['end'], 'end': grouping[i]['start'], 'tag': 'O'}])        allgr_filled.append(grouped_filled)    for group in allgr_filled:        group[0]['token_start'] = 0        for i in range(1, len(group)):            group[i]['token_start'] = group[i - 1]['token_start'] + len(nlp(group[i - 1]['text']))        for i in range(len(group)):            group[i]['tokens'] = [str(tok) for tok in nlp(group[i]['text'])]            group[i]['token_end'] = group[i]['token_start'] + len(group[i]['tokens']) - 1            if group[i]['tag'] == 'O':                group[i]['BIO-Tags'] = [group[i]['tag']] * len(group[i]['tokens'])            else:                group[i]['BIO-Tags'] = ['B-' + group[i]['tag']] + ['I-' + group[i]['tag']] * (                            len(group[i]['tokens']) - 1)    all_tokens = []    all_tags = []    for group in allgr_filled:        tokss = []        tagss = []        for item in group:            tokss.extend(item['tokens'])            tagss.extend(item['BIO-Tags'])        all_tokens.append(tokss)        all_tags.append(tagss)    ENTITY_DATA = [{'tokens': x, 'ner_tags': y} for (x, y) in zip(all_tokens, all_tags)]    for grp in ENTITY_DATA:        blnks = [i for i in range(len(grp['tokens'])) if grp['tokens'][i] == " " or grp['tokens'][i] == "  "]        blnks.reverse()        #print(blnks)        for idx in blnks:            grp['tokens'].pop(idx)            grp['ner_tags'].pop(idx)    return ENTITY_DATAPOOL_Entities=[]for chaps in range(1,11):    print('Chapter_' + str(chaps))    a = pool_builder_entity('Chapter_' + str(chaps))    POOL_Entities.extend(a)all_tokens = [b['tokens'] for b in POOL_Entities]all_ner_tags = [c['ner_tags'] for c in POOL_Entities]data_len = len(all_tokens)training_len = round(data_len*0.7)#training_len = round(data_len)training_tokens = all_tokens[:training_len]valid_tokens = all_tokens[training_len:]training_tags = all_ner_tags[:training_len]valid_tags = all_ner_tags[training_len:]def EntityBreaker(split, tokens, ner_tags):    with open('R_POOLED_ER_'+split+'.txt', 'w', encoding="utf-8") as f:        for idx in range(len(tokens)):            f.write('-DOCSTART- -X- O O\n\n')            for (x,y) in zip(tokens[idx], ner_tags[idx]):                f.write(str(x)+ '\t' + str(y) + '\n')            f.write('\n')EntityBreaker('train', training_tokens, training_tags)EntityBreaker('validate', valid_tokens, valid_tags)