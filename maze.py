from tkinter import *
import tkinter.messagebox as messagebox
import random
import copy
import time

WALL  = 1
PATH  = 2
START = 3
END   = 4
MAN   = 5

MOVE_UP    = 1
MOVE_DOWN  = 2
MOVE_LEFT  = 3
MOVE_RIGHT = 4

def in_stack(item, stack):
    for i in stack:
        if item == i:
            return True
    return False

# 迷宫出路自动探测
def auto_walk():
    # 记当前位置为起点S，依次沿着上/下/左/右固定的4个方向尝试往前走
    # 　如果沿其中任一方向可以走，且该方向没有走过
    # 　　沿该方向走一步，新位置记为X
    # 　　如果X是终点，停止
    # 　　将新位置X压栈，并设定为当前位置
    # 　如果所方向都不能走
    # 　　标记当前位置为不可走，回退到上一步
    # 　　如果退到了起点S，退出
    global cur_row, cur_col
    maze_status = copy.deepcopy(maze_num) # 深复制
    if maze_status[cur_row][cur_col] == END: # 如果站在终点，则回到起点
        cur_row = cur_col = 1
    stack = [(cur_row,cur_col)]

    found = False
    while True:
        # 前方单元格子是路并且没有走过，才往前走
        if maze_status[cur_row-1][cur_col] != WALL and not in_stack((cur_row-1,cur_col), stack):
            # MOVE_UP
            cur_row -= 1
            stack.append((cur_row,cur_col))
            if maze_status[cur_row][cur_col] == END:
                found = True
                break
        elif maze_status[cur_row+1][cur_col] != WALL and not in_stack((cur_row+1,cur_col), stack):
            # MOVE_DOWN
            cur_row += 1
            stack.append((cur_row,cur_col))
            if maze_status[cur_row][cur_col] == END:
                found = True
                break
        elif maze_status[cur_row][cur_col-1] != WALL and not in_stack((cur_row,cur_col-1), stack):
            # MOVE_LEFT
            cur_col -= 1
            stack.append((cur_row,cur_col))
            if maze_status[cur_row][cur_col] == END:
                found = True
                break
        elif maze_status[cur_row][cur_col+1] != WALL and not in_stack((cur_row,cur_col+1), stack):
            # MOVE_RIGHT
            cur_col += 1
            stack.append((cur_row,cur_col))
            if maze_status[cur_row][cur_col] == END:
                found = True
                break
        else:
            maze_status[cur_row][cur_col] = WALL
            if len(stack) != 0:
                stack.pop()
                if len(stack) == 0:
                    messagebox.showinfo('走迷宫', '找不到路！')
                    break
                else:
                    cur_row, cur_col = stack[-1]
            else:
                messagebox.showinfo('走迷宫', '找不到路！')
                break
    if found:
        for j,i in enumerate(stack):
            # print(i)
            if j != 0 and j != len(stack)-1:
                x, y = i
                canvas.itemconfig(maze_image[x][y], image=image_path_found)
                canvas.update()
                time.sleep(0.1)
        cur_row, cur_col = stack[0] # 恢复当前位置

# 从上/下/左/右四个方向可走的格子中任选一个返回
def find_neighbor_free_cell(cur_row, cur_col, visited_cells):
    available_cell_list = []
    for i,j in [(0,2),(0,-2),(2,0),(-2,0)]:
        next_row, next_col = cur_row+i, cur_col+j
        if 0<=next_row<row and 0<=next_col<col and (next_row,next_col) not in visited_cells:
            available_cell_list.append((next_row,next_col))
    list_size = len(available_cell_list)
    if list_size == 0:
        return None
    else:
        return available_cell_list[random.randint(0,list_size-1)]

# 随机生成迷宫地图：随机打通孤立的格子0之间的连接(用0连接)
#                       行号(y) 空白行号(x)
# 1 1 1 1 1 1 1 1 1 1 1 -- 0
# 1 0 1 0 1 0 1 0 1 0 1 -- 1      1 -- 关系: y=2x-1
# 1 1 1 1 1 1 1 1 1 1 1 -- 2
# 1 0 1 0 1 0 1 0 1 0 1 -- 3      2
# 1 1 1 1 1 1 1 1 1 1 1 -- 4
# 1 0 1 0 1 0 1 0 1 0 1 -- 5      3
# 1 1 1 1 1 1 1 1 1 1 1 -- 6
# 1 0 1 0 1 0 1 0 1 0 1 -- 7      4 -- 空白行数
# 1 1 1 1 1 1 1 1 1 1 1 -- 8
#
# 设迷宫大小为R行C列，R/C分别表示刚开始格子0的行/列数
# 格子0之间还有墙壁，所以最终产生的二维数组大小实际为 2R+1 * 2C+1
#
# 随机选择某个格子0作为当前访问格子(记为A)，同时把该格子放入已经访问列表
# 循环以下操作，直到所有的格子0都被访问到
#   在A的邻近四周(上下左右)，随机查找一个没有在访问列表中的格子0(记为B)
#   如果找到
#     把A和B中间的墙打通(置为0)，并把B作为当前访问格子，加入访问列表
#   如果没有找到 -- A周围所有的格子0都已经访问过
#     从已访问的列表中，随机选取一个作为当前访问格子
def generate_random_map():
    global cur_row, cur_col
    for i in range(row):
        for j in range(col):
            if i % 2 == 1 and j % 2 == 1:
                maze_num[i][j] = PATH # 生成格子0
            else:
                maze_num[i][j] = WALL

    visited_cells = set()
    cur_row = 2*random.randint(1,row_blank) - 1
    cur_col = 2*random.randint(1,col_blank) - 1
    visited_cells.add((cur_row, cur_col))

    # 随机生成迷宫地图
    while len(visited_cells) != row_blank*col_blank:
        free_cell = find_neighbor_free_cell(cur_row, cur_col, visited_cells)
        if free_cell:
            visited_cells.add(free_cell)
            x, y = free_cell
            maze_num[(cur_row+x)//2][(cur_col+y)//2] = PATH # 打通墙壁
            cur_row, cur_col = x, y
        else:
            # 从已访问列表中随机选取一个格子(记为C)，条件是C四周有未被访问过的格子0(记为D)
            # 如果D存在
            #   把C和D中间的墙打通(置为0)，把D加入已访问格子列表
            # 如果D不存在
            #   说明所有格子都加入进了访问列表，退出
            if len(visited_cells) == row_blank*col_blank:
                print('生成树已遍历所有格子')
                break
            else:
                for i,j in visited_cells:
                    free_cell = find_neighbor_free_cell(i, j, visited_cells)
                    if free_cell:
                        break
                visited_cells.add(free_cell)
                x, y = free_cell
                maze_num[(i+x)//2][(j+y)//2] = PATH # 打通墙壁
                cur_row, cur_col = x, y

    cur_row, cur_col = 1, 1
    maze_num[cur_row][cur_col] = MAN
    maze_num[2*row_blank-1][2*col_blank-1] = END

    # 画迷宫
    for i in range(row):
        for j in range(col):
            maze_image[i][j] = canvas.create_image(img_size/2+img_size*j, img_size/2+img_size*i, image=image_map[maze_num[i][j]])

def can_move(cur_row, cur_col, direction):
    forward_row = cur_row
    forward_col = cur_col
    # 计算下一位置
    if direction == MOVE_LEFT:
        forward_col -= 1
    elif direction == MOVE_RIGHT:
        forward_col += 1
    elif direction == MOVE_UP:
        forward_row -= 1
    elif direction == MOVE_DOWN:
        forward_row += 1

    # 判断是否可以走到下一位置
    if maze_num[forward_row][forward_col] == PATH: # 前方是路，可以走
        return True
    elif maze_num[forward_row][forward_col] == END: # 前方是终点，可以走
        return True
    elif maze_num[forward_row][forward_col] == START: # 前方是起点，可以走
        return True
    else: # 前方必定是墙，不能走
        return False

def move(cur_row, cur_col, direction):
    global cur_position_shape
    forward_row = cur_row
    forward_col = cur_col
    # 计算下一位置
    if direction == MOVE_LEFT:
        forward_col -= 1
    elif direction == MOVE_RIGHT:
        forward_col += 1
    elif direction == MOVE_UP:
        forward_row -= 1
    elif direction == MOVE_DOWN:
        forward_row += 1

    # 往前走
    if maze_num[forward_row][forward_col] == PATH: # 前方是路
        if cur_position_shape == START: # 来自起点 -- 排除来自终点（已经赢了）
            canvas.itemconfig(maze_image[cur_row][cur_col], image=image_start)
        else: # 来自空地
            canvas.itemconfig(maze_image[cur_row][cur_col], image=image_path)
        canvas.itemconfig(maze_image[forward_row][forward_col], image=image_man)
        maze_num[cur_row][cur_col] = cur_position_shape
        maze_num[forward_row][forward_col] = MAN
        cur_position_shape = PATH # 现在站在地板上
    elif maze_num[forward_row][forward_col] == END: # 前方是终点
        canvas.itemconfig(maze_image[cur_row][cur_col], image=image_path) # 只能来自空地
        canvas.itemconfig(maze_image[forward_row][forward_col], image=image_man)
        messagebox.showinfo('走迷宫', '恭喜你，成功了！')
    elif maze_num[forward_row][forward_col] == START: # 前方是起点
        canvas.itemconfig(maze_image[cur_row][cur_col], image=image_path) # 只能来自空地
        canvas.itemconfig(maze_image[forward_row][forward_col], image=image_man)
        maze_num[cur_row][cur_col] = cur_position_shape
        maze_num[forward_row][forward_col] = MAN
        cur_position_shape = START # 现在站在起点
    else:
        pass

def up_key(event):
    global cur_row, cur_col
    if not can_move(cur_row, cur_col, MOVE_UP):
        return
    move(cur_row, cur_col, MOVE_UP)
    cur_row -= 1

def down_key(event):
    global cur_row, cur_col
    if not can_move(cur_row, cur_col, MOVE_DOWN):
        return
    move(cur_row, cur_col, MOVE_DOWN)
    cur_row += 1

def left_key(event):
    global cur_row, cur_col
    if not can_move(cur_row, cur_col, MOVE_LEFT):
        return
    move(cur_row, cur_col, MOVE_LEFT)
    cur_col -= 1

def right_key(event):
    global cur_row, cur_col
    if not can_move(cur_row, cur_col, MOVE_RIGHT):
        return
    move(cur_row, cur_col, MOVE_RIGHT)
    cur_col += 1


# 算法逻辑开始
print('迷宫游戏\n运行环境：Python3 & Windows 7/10\n使用方法：python maze.py large/other_word 迷宫空白行数(R) 迷宫空白列数(C)\n按 Enter 继续，按 Ctrl+C 退出')
input()

random.seed()

# 解析命令行参数
large_image = False

# 脚本[0] 'large'[1] 空白行数[2] 空白列数[3] ...
if len(sys.argv)>=2 and sys.argv[1]=='large':
    large_image = True

if large_image:
    img_size = 31 # 设置图片大小
else:
    img_size = 15

if large_image:
    row_blank = 10
    col_blank = 10
else:
    row_blank = 23
    col_blank = 40

# 脚本[0] 'large'[1] 空白行数[2] 空白列数[3] ...
if len(sys.argv) >= 4:
    row_blank = int(sys.argv[2])
    col_blank = int(sys.argv[3])

row = 2*row_blank + 1
col = 2*col_blank + 1

# 保存迷宫的格子状态和显示图形
maze_num = [[WALL for col in range(col)] for row in range(row)]
maze_image = [[0 for col in range(col)] for row in range(row)]

cur_row = 1 # 起始位置固定
cur_col = 1

# 搬运工所站位置的形状
cur_position_shape = START

root = Tk()
root.title("走迷宫")

# PhotoImage 放在 Tk() 后面
image_map = {}
if large_image:
    image_map[WALL] = PhotoImage(file="wall.png")
    image_map[PATH] = PhotoImage(file="path.png")
    image_map[MAN] = PhotoImage(file="man.png")
    image_map[START] = PhotoImage(file="start.png")
    image_map[END] = PhotoImage(file="end.png")
else:
    image_map[WALL] = PhotoImage(file="small_wall.png")
    image_map[PATH] = PhotoImage(file="small_path.png")
    image_map[MAN] = PhotoImage(file="small_man.png")
    image_map[START] = PhotoImage(file="small_start.png")
    image_map[END] = PhotoImage(file="small_end.png")

if large_image:
    image_wall = PhotoImage(file="wall.png")
    image_path = PhotoImage(file="path.png")
    image_path_found = PhotoImage(file="path_found.png")
    image_man = PhotoImage(file="man.png")
    image_start = PhotoImage(file="start.png")
    image_end = PhotoImage(file="end.png")
else:
    image_wall = PhotoImage(file="small_wall.png")
    image_path = PhotoImage(file="small_path.png")
    image_path_found = PhotoImage(file="small_path_found.png")
    image_man = PhotoImage(file="small_man.png")
    image_start = PhotoImage(file="small_start.png")
    image_end = PhotoImage(file="small_end.png")

frame = Frame(root)
Label(frame, justify=LEFT, text=" ").pack(side=LEFT)
Button(frame, text ="自动走迷宫", command = auto_walk).pack(side=LEFT)
Label(frame, justify=LEFT, text=" ").pack(side=LEFT)
Button(frame, text ="重新开始", command = generate_random_map).pack(side=LEFT)
Label(frame, justify=LEFT, text=" ").pack(side=LEFT)
label = Label(frame, justify=LEFT, text="玩法：使用【上/下/左/右】方向键控制笑脸的行走方向，直到走到迷宫出口(Exit)算赢\n点击“自动走迷宫”按钮，则游戏会自动找出通往迷宫出口的路\n点击“重新开始”按钮，将重新随机生成一个迷宫地图")
label.pack(side=LEFT)
frame.pack(fill=BOTH, expand=YES)

canvas = Canvas(root, bg='white', width=1400, height=700)
#canvas = Canvas(root, bg='white', width=600, height=600)
canvas.pack()

root.bind("<Left>", left_key)
root.bind("<Up>", up_key)
root.bind("<Right>", right_key)
root.bind("<Down>", down_key)

generate_random_map()

root.mainloop()
