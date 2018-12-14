import re


def rv_translate():
    rv_str = ''
    with open('./sznewupdate_dbo_PackageUpdate.sql', 'r+') as f:
        content = f.read()

        old_str = r'sznewupdate.dbo.PackageUpdate'
        new_str = 'sznewupdate.rversion'
        content = re.sub(old_str, new_str, content)

        old_str = r'\(readername, Version, Title, Content, Time, isupdate, Vmiddle, sort\)'
        new_str = '(create_time, reader_id, version, title, description, update_time, state, depend_version, sort)'
        content = re.sub(old_str, new_str, content)

        old_str = r"\('86E'"
        new_str = "(null, 1"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86D'"
        new_str = "(null, 2"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86K'"
        new_str = "(null, 3"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86E-twostore'"
        new_str = "(null, 4"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86D-twostore'"
        new_str = "(null, 5"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86e-plus'"
        new_str = "(null, 6"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86Fplus'"
        new_str = "(null, 7"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86G'"
        new_str = "(null, 8"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86b'"
        new_str = "(null, 9"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86I'"
        new_str = "(null, 10"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86H'"
        new_str = "(null, 11"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86k_axplight'"
        new_str = "(null, 12"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86I_wanxin'"
        new_str = "(null, 13"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86G_xiyue'"
        new_str = "(null, 14"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('88A'"
        new_str = "(null, 15"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('bookeen'"
        new_str = "(null, 16"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86M'"
        new_str = "(null, 17"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86L'"
        new_str = "(null, 18"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('888a'"
        new_str = "(null, 19"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86I-xiyue'"
        new_str = "(null, 20"
        content = re.sub(old_str, new_str, content)
        old_str = r"\('86L_white'"
        new_str = "(null, 21"
        content = re.sub(old_str, new_str, content)

        rv_str += content

    with open('./rversion.sql', 'w+') as f:
        f.write(rv_str)


def pack_translate():
    pack_str = ''
    with open('./sznewupdate_dbo_Packagelist.sql', 'r+') as f:
        content = f.read()

        old_str = r"sznewupdate.dbo.Packagelist"
        new_str = "sznewupdate.package"
        content = re.sub(old_str, new_str, content)

        old_str = r"\(baseversion, url, Md5, Model, PID\)"
        new_str = "(create_time, update_time, base_version, pack, md5, model, pid, state)"
        content = re.sub(old_str, new_str, content)

        old_str = r"VALUES \("
        new_str = "VALUES (null, null, "
        content = re.sub(old_str, new_str, content)

        old_str = r", 2\);"
        new_str = ", 1, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 3\);"
        new_str = ", 2, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 4\);"
        new_str = ", 3, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 5\);"
        new_str = ", 4, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 6\);"
        new_str = ", 5, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 7\);"
        new_str = ", 6, 0);"
        content = re.sub(old_str, new_str, content)
        # old_str = r", 8\);"
        # new_str = ", 7, 0);"
        # content = re.sub(old_str, new_str, content)
        old_str = r", 9\);"
        new_str = ", 7, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 10\);"
        new_str = ", 8, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 11\);"
        new_str = ", 9, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 13\);"
        new_str = ", 10, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 16\);"
        new_str = ", 11, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 17\);"
        new_str = ", 12, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 19\);"
        new_str = ", 13, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 20\);"
        new_str = ", 14, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 22\);"
        new_str = ", 15, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 23\);"
        new_str = ", 16, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 25\);"
        new_str = ", 17, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 28\);"
        new_str = ", 18, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 29\);"
        new_str = ", 19, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 30\);"
        new_str = ", 20, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 32\);"
        new_str = ", 21, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 33\);"
        new_str = ", 22, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 40\);"
        new_str = ", 23, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 43\);"
        new_str = ", 24, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 44\);"
        new_str = ", 25, 0);"
        content = re.sub(old_str, new_str, content)

        pack_str += content

    with open('./package.sql', 'w+') as f:
        f.write(pack_str)


if __name__ == '__main__':
    input('提示:删除packageupdate表86F-plus记录,同时要将rversion的state改成2')

    '''
    删除以下升级包记录
    base_version     model                 pid
    5.0              dangdang86d           2
    5.0              dangdang86d_flaxp     2
    4.0              epd86i_flaxfeibao     15
    4.0              epd86i_flaxfeibao     24
    1.0              epd86g                7
    1.0              epd86g                14
    1.0              epd86g                23
    1.0              epd86g                25
    '''

    pack_translate()
    rv_translate()