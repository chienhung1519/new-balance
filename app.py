import streamlit as st
import pandas as pd

# 月份比對
mapping= {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DEC"
}

# 型號確認
def check_ftw(text):
    if len(text) >= 6:
        if text[0] in ["M", "W", "U", "G", "Y", "P", "I", "K"]:
            if text not in ["Inline", "MADE Teddy Santis", "Grey 1906 only", "Inline MADE", "Unisex", "INLINE SKU"]:
                return True
    return False

def check_app(text):
    if len(text) >= 9:
        if text[0] in ["M", "W", "Y", "5", "6"]:
            if text[1] in ["J", "T", "S", "P", "V", "D", "K", "B", "8"]:
                if text != "WS/HHG EXCLUSIVE":
                    return True
        if text[:2] in ["AM", "AW"]:
            if text[2] in ["J", "T", "S", "P", "V", "D", "K", "B", "8"]:
                if text != "WS/HHG EXCLUSIVE":
                    return True
        return False

col1, col2, col3 = st.columns([3,4,3])
with col2:
    st.title("New Balance")

category = st.radio("Category：", ("APP", "FTW"), index=0)

st.info("表頭名稱須為『PSI Style』和『New Launch Month』")

# 上傳核對清單
check_file = st.file_uploader("請上傳核對清單")
if check_file is not None:
    df_check = pd.read_excel(check_file)
    check_dict = {}
    for i, row in df_check.iterrows():
        if not pd.isna(row["New Launch Month"]):
            check_dict[row["PSI Style"]] = mapping[row["New Launch Month"].month]
        else:
            check_dict[row["PSI Style"]] = ""

# 上傳上市月份圖
market_file = st.file_uploader("請上傳上市月份圖")
if market_file is not None:
    df_market = pd.read_excel(market_file, sheet_name=None, engine='openpyxl')
    sheet = pd.ExcelFile(market_file, engine='openpyxl')

    # st.write(check_dict)

    st.warning(
        "Error message  \n  not in skulist：上市月份圖的型號不存在於 SKU List (注意空白)  \n  launch month is empty：SKU List 上的 SKU 的上市月份為空白  \n  launch month error：上市月份圖與 SKU List 的上市月份不一致"
    )


    # 開始比對
    log = []
    cur_month = ""
    for s_name in sheet.sheet_names:
        st.write(f"**Start scanning sheet {s_name}**")
        table = df_market.get(s_name)
        table = table.T
        for i, row in table.iterrows():
            for item in row:
                if pd.isna(item):
                    continue

                item = str(item)

                if item in mapping.values():
                    cur_month = item
                    continue

                if category == "FTW":
                    check = check_ftw(item)
                else:
                    check = check_app(item)
                if check:
                    if item not in check_dict:
                        st.write(f"{item} not in skulist!")
                        log.append([s_name, item, "not in skulist!"])
                    elif check_dict[item] == "":
                        st.write(f"{item} launch month is empty!")
                        log.append([s_name, item, "launch month is empty!"])
                    elif check_dict[item] != cur_month:
                        st.write(f"{item} launch month error!")
                        log.append([s_name, item, "launch month error!"])                            

    st.write("Finished!")

    # Download
    @st.cache
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False).encode('utf-8')

    df_download = pd.DataFrame(log, columns=["sheet", "PSI Style", "message"])
    csv = convert_df(df_download)

    st.download_button(
        label="下載檔案",
        data=csv,
        file_name='error.csv',
        mime='text/csv',
    )