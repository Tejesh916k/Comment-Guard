import traceback

try:
    import pandas as pd
    
    path = 'data/training_data_telugu-hate.xlsx'
    print(f"Loading {path}...")
    df = pd.read_excel(path)
    print(f"Original shape: {df.shape}")
    
    # 1. Back up the original file just in case
    df.to_excel('data/training_data_telugu-hate_backup.xlsx', index=False)
    
    # Clean duplicates and nans
    df = df.dropna(subset=['Comments', 'Label'])
    df['Comments'] = df['Comments'].astype(str).str.strip()
    df['Label'] = df['Label'].astype(str).str.strip().str.lower()
    df = df[df['Label'].isin(['hate', 'non-hate'])]
    df = df.drop_duplicates(subset=['Comments'], keep='first')
    
    print(f"Shape after cleaning: {df.shape}")
    
    # New words
    toxic = [
        "rey mental puku", "ni edava veshalu", "konda erri hook", "thu ni brathuku cheda", "panimashiva ra nuvu", 
        "erri puku nayala", "nuvu oka pedda jaffa", "siggu ledu ra neeku", "pichi pulka gadu", "waste fellow ra nuvu",
        "dengay ra lathkor", "ni yamma kadupula koti", "adangi vedhava", "gudda balupu", "boku gadu vidu",
        "rey chetha na kodaka", "poramboku nayala", "ni mokam chudu elagundo", "chapri gadu lanjodka", "lavada lo panulu",
        "modda em kadu le", "pachi boothulu tidutha", "daridrudu", "tuppas gadu", "chavata chavata",
        "mental gadu ra vidu", "sannasi", "bewarse gadu", "ne bondha ra ne bondha", "rey puku",
        "vedava sannaasi", "guddalo em ledha", "ni amma", "ni abba", "rey lanjodoka", "addamina waste gadu",
        "rotta gadu", "faltu gadu", "picha light teesko ra puku", "lathkor gadu", "erri pusa",
        "bazar munda", "rey kojja nayala", "ni ayya ki cheppu", "solu gadu", "sollu cheppaku nayala",
        "arey howle", "bhadcow gadu", "puka musko", "rey ni amma", "denga beta",
        "ni puku lo na modda", "erri guda", "nuvvu oka waste puku", "ni yabba", "dunnapothu nayala",
        "munda mokam", "sulli gadu", "arey erri", "pedda puku", "mental na kodaka", "lanja kodaka",
        "ni amma ranku", "chethana kodaka", "musali puku", "gudda chimputha", "ni amma ninnu kaninda",
        "rey neeku guddalo dammu leda", "ni mokam meda umma", "chepaleni boothulu", "thu ni bathuku", "kukka brathuku",
        "ni bathuku bus stand", "picchi puku", "hook gani laga unnav", "gadida kodaka",
        "donga puku", "munda edava", "musko ra jaffa", "bocchu gadu", "ni ayya puku", "naa modda guduvu",
        "lavadalo comments", "item gani laga unnav", "loffer gadu", "ni face ki dippa okate takkuva", "pakodi gadu",
        "mental hospital ki ellu", "rey pichi guda", "bithiri", "buffoon gadu", "420 gadu",
        "ne kamma", "ni bondha pettu", "kothi na kodaka", "labor na kodaka", "signal daggara adukko", "Footpath gadu"
    ]
    
    safe = [
        "super undi bro", "congrats macha", "all the best ra", "chala bagundi", "kekaa", 
        "thanks anna", "subram ga undi", "awesome work", "good job keep it up", "nice explanation",
        "this is very helpful", "mee video lu ante chala ishtam", "first comment ra", "video super", "nice editing",
        "super ga chepparu", "meeru inka goppavallu avvali", "waiting for next part", "good morning everyone", "have a nice day",
        "really nice bro", "bhale cheppav", "good point", "manchi maata", "exactly macha",
        "agreed", "well said anna", "proud of you", "jai hind", "super hit",
        "very informative", "hats off to you", "good lesson learned", "superb acting", "next level",
        "mind blowing performance", "keep soaring high", "bagundi", "baga chesaaru", "congratulations brother",
        "so beautiful", "very nice song", "loved this", "manchi content idhi", "thank you so much",
        "keep going", "amazing as always", "very true words", "good luck", "edo oka roju sadhistavu",
        "meeru goppa anna", "salute anna", "inspiring video", "bhale tisaaru", "cinematography peaks",
        "this made my day", "chala happy ga undi", "super star nvvu", "naaku idi chala use aindi", "respect",
        "god bless you", "super anna", "keep doing videos", "nenu subscribe chesa", "like kottandi",
        "miku manchi jargali", "great progress", "awesome efforts", "very nice tutorial", "fantastic",
        "proud moment", "excellent work", "bhale undi kada", "super ga navvu", "nice smile",
        "thanks for your support", "manchi advice", "helpful tips", "very clear", "super bro super",
        "love from hyd", "amazing talent", "keep rocking", "gret job", "so soothing",
        "wonderful video", "sweet comments", "very kind of you", "thank you akka", "wow super",
        "masterpiece", "great info", "good stuff", "so positive", "happy for you", "best wishes",
        "take care", "always supporting you", "superb explanation", "nice tutorial bro", "you are the best"
    ]
    
    # Map to new rows
    new_rows = []
    
    for t in toxic:
        new_rows.append({'S.No': 'AUGMENTED_HATE', 'Comments': t, 'Label': 'hate'})
    for s in safe:
        new_rows.append({'S.No': 'AUGMENTED_SAFE', 'Comments': s, 'Label': 'non-hate'})
        
    augment_df = pd.DataFrame(new_rows)
    final_df = pd.concat([df, augment_df], ignore_index=True)
    
    # Overwrite
    final_df.to_excel(path, index=False)
    print(f"Final shape: {final_df.shape}")
    print("✅ Augmentation complete! Successfully wrote to Excel.")

except Exception as e:
    with open('error_log.txt', 'w') as f:
        f.write(traceback.format_exc())
    print("Script failed. See error_log.txt")
