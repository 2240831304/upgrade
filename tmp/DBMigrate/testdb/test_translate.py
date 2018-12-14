import re


def reader_translate():
    reader_str = ''
    with open('./sznewupdate_test_dbo_reader.sql', 'r+') as f:
        content = f.read()

        old_str = r'sznewupdate_test.dbo.reader'
        new_str = 'sznewupdate_test.reader'
        content = re.sub(old_str, new_str, content)

        old_str = r'\(readername, sort\)'
        new_str = '(create_time, update_time, reader_name, sort, state)'
        content = re.sub(old_str, new_str, content)

        old_str = r"VALUES \("
        new_str = "VALUES (null, null, "
        content = re.sub(old_str, new_str, content)

        old_str = r"\);"
        new_str = " ,0);"
        content = re.sub(old_str, new_str, content)

        reader_str +=content

    with open('./reader.sql', 'w+') as f:
        f.write(reader_str)


def rv_translate():
    rv_str = ''
    with open('./sznewupdate_test_dbo_PackageUpdate.sql', 'r+') as f:
        content = f.read()

        old_str = r'sznewupdate_test.dbo.PackageUpdate'
        new_str = 'sznewupdate_test.rversion'
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
    with open('./sznewupdate_test_dbo_Packagelist.sql', 'r+') as f:
        content = f.read()

        old_str = r"sznewupdate_test.dbo.Packagelist"
        new_str = "sznewupdate_test.package"
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
        old_str = r", 8\);"
        new_str = ", 7, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 9\);"
        new_str = ", 8, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 10\);"
        new_str = ", 9, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 11\);"
        new_str = ", 10, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 13\);"
        new_str = ", 11, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 14\);"
        new_str = ", 12, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 15\);"
        new_str = ", 13, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 16\);"
        new_str = ", 14, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 17\);"
        new_str = ", 15, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 18\);"
        new_str = ", 16, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 19\);"
        new_str = ", 17, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 20\);"
        new_str = ", 18, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 21\);"
        new_str = ", 19, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 22\);"
        new_str = ", 20, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 23\);"
        new_str = ", 21, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 24\);"
        new_str = ", 22, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 25\);"
        new_str = ", 23, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 28\);"
        new_str = ", 24, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 29\);"
        new_str = ", 25, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 30\);"
        new_str = ", 26, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 31\);"
        new_str = ", 27, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 32\);"
        new_str = ", 28, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 33\);"
        new_str = ", 29, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 34\);"
        new_str = ", 30, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 35\);"
        new_str = ", 31, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 36\);"
        new_str = ", 32, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 39\);"
        new_str = ", 33, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 40\);"
        new_str = ", 34, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 42\);"
        new_str = ", 35, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 43\);"
        new_str = ", 36, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 44\);"
        new_str = ", 37, 0);"
        content = re.sub(old_str, new_str, content)
        old_str = r", 45\);"
        new_str = ", 38, 0);"
        content = re.sub(old_str, new_str, content)

        pack_str += content

    with open('./package.sql', 'w+') as f:
        f.write(pack_str)

if __name__ == '__main__':
    input('提示:在数据库中将rversion的状态1改成2')
    reader_translate()
    rv_translate()
    pack_translate()