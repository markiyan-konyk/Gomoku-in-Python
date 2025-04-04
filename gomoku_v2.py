import tkinter as tk
from tkinter import messagebox, font
import time

class GomokuGUI:
    def __init__(self, master, board_size=8):
        self.master = master
        self.board_size = board_size
        self.cell_size = 50
        self.padding = 20
        
        # Set up the main window
        master.title("Gomoku")
        master.resizable(False, False)
        
        # Calculate canvas size
        canvas_width = board_size * self.cell_size + 2 * self.padding
        canvas_height = board_size * self.cell_size + 2 * self.padding
        
        # Create game board and UI elements
        self.init_ui(canvas_width, canvas_height)
        
        # Create empty board
        self.board = self.make_empty_board(board_size)
        
        # Initial state
        self.game_over = False
        self.waiting_for_computer = False
        self.info_text = "Game started. Black (Computer) plays first."
        self.update_info()
        
        # Start the game
        self.master.after(500, self.computer_move)
    
    def init_ui(self, width, height):
        # Create frame for the board
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(pady=10)
        
        # Create canvas for the board
        self.canvas = tk.Canvas(self.board_frame, width=width, height=height, bg='#DDBB88')
        self.canvas.pack()
        
        # Create info frame below the board
        self.info_frame = tk.Frame(self.master)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        # Create info label
        self.info_label = tk.Label(self.info_frame, text="", font=('Arial', 12))
        self.info_label.pack()
        
        # Create analysis frame
        self.analysis_frame = tk.Frame(self.master)
        self.analysis_frame.pack(fill=tk.X, pady=5)
        
        # Create analysis text widgets
        self.black_analysis = tk.Text(self.analysis_frame, height=5, width=30, font=('Courier', 10))
        self.black_analysis.grid(row=0, column=0, padx=5)
        
        self.white_analysis = tk.Text(self.analysis_frame, height=5, width=30, font=('Courier', 10))
        self.white_analysis.grid(row=0, column=1, padx=5)
        
        # Create restart button
        self.restart_button = tk.Button(self.master, text="Restart Game", command=self.restart_game)
        self.restart_button.pack(pady=10)
        
        # Draw grid
        self.draw_grid()
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_canvas_click)
    
    def draw_grid(self):
        # Clear canvas
        self.canvas.delete("grid")
        
        # Draw horizontal lines
        for i in range(self.board_size + 1):
            y = self.padding + i * self.cell_size
            self.canvas.create_line(
                self.padding, y, 
                self.padding + self.board_size * self.cell_size, y,
                tags="grid"
            )
        
        # Draw vertical lines
        for i in range(self.board_size + 1):
            x = self.padding + i * self.cell_size
            self.canvas.create_line(
                x, self.padding,
                x, self.padding + self.board_size * self.cell_size,
                tags="grid"
            )
        
        # Add coordinate labels
        for i in range(self.board_size):
            # Horizontal labels (numbers)
            y_pos = self.padding + i * self.cell_size + self.cell_size // 2
            self.canvas.create_text(
                self.padding // 2, y_pos,
                text=str(i),
                font=('Arial', 10),
                tags="grid"
            )
            
            # Vertical labels (letters)
            x_pos = self.padding + i * self.cell_size + self.cell_size // 2
            self.canvas.create_text(
                x_pos, self.padding // 2,
                text=str(i),
                font=('Arial', 10),
                tags="grid"
            )
    
    def draw_board(self):
        # Clear stones
        self.canvas.delete("stone")
        
        # Draw stones
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.board[y][x] != " ":
                    self.draw_stone(x, y, self.board[y][x])
    
    def draw_stone(self, x, y, color):
        # Calculate pixel coordinates
        center_x = self.padding + x * self.cell_size + self.cell_size // 2
        center_y = self.padding + y * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 2
        
        # Draw stone
        fill_color = "black" if color == "b" else "white"
        outline_color = "white" if color == "b" else "black"
        
        self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            fill=fill_color, outline=outline_color, width=2,
            tags="stone"
        )
    
    def on_canvas_click(self, event):
        if self.game_over or self.waiting_for_computer:
            return
        
        # Convert pixel coordinates to board coordinates
        x = (event.x - self.padding) // self.cell_size
        y = (event.y - self.padding) // self.cell_size
        
        # Check if click is within the board boundaries
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            # Check if the cell is empty
            if self.board[y][x] == " ":
                # Make the player's move
                self.board[y][x] = "w"
                self.draw_board()
                
                self.info_text = f"You placed at ({y}, {x})"
                self.update_info()
                self.update_analysis()
                
                # Check if game is over
                result = self.is_win(self.board)
                if result != "Continue":
                    self.game_over = True
                    self.show_game_result(result)
                    return
                
                # Computer's turn
                self.waiting_for_computer = True
                self.info_text = "Computer is thinking..."
                self.update_info()
                self.master.after(500, self.computer_move)
    
    def computer_move(self):
        if self.is_empty(self.board):
            # First move in the center
            move_y = self.board_size // 2
            move_x = self.board_size // 2
        else:
            # Use the AI to find the best move
            move_y, move_x = self.search_max(self.board)
        
        # Make the computer's move
        self.board[move_y][move_x] = "b"
        self.draw_board()
        
        self.info_text = f"Computer placed at ({move_y}, {move_x})"
        self.update_info()
        self.update_analysis()
        
        # Check if game is over
        result = self.is_win(self.board)
        if result != "Continue":
            self.game_over = True
            self.show_game_result(result)
            return
        
        self.waiting_for_computer = False
    
    def show_game_result(self, result):
        messagebox.showinfo("Game Over", result)
        self.info_text = f"Game over: {result}. Click Restart to play again."
        self.update_info()
    
    def restart_game(self):
        # Clear the board
        self.board = self.make_empty_board(self.board_size)
        self.draw_board()
        
        # Reset game state
        self.game_over = False
        self.waiting_for_computer = False
        
        # Update UI
        self.info_text = "Game restarted. Black (Computer) plays first."
        self.update_info()
        self.black_analysis.delete(1.0, tk.END)
        self.white_analysis.delete(1.0, tk.END)
        
        # Start with computer's move
        self.master.after(500, self.computer_move)
    
    def update_info(self):
        self.info_label.config(text=self.info_text)
    
    def update_analysis(self):
        # Clear previous analysis
        self.black_analysis.delete(1.0, tk.END)
        self.white_analysis.delete(1.0, tk.END)
        
        # Add headers
        self.black_analysis.insert(tk.END, "Black stones (Computer)\n")
        self.white_analysis.insert(tk.END, "White stones (You)\n")
        
        # Add analysis for black
        for i in range(2, 6):
            open_b, semi_open_b = self.detect_rows(self.board, "b", i)
            self.black_analysis.insert(tk.END, f"Open rows of length {i}: {open_b}\n")
            self.black_analysis.insert(tk.END, f"Semi-open rows of length {i}: {semi_open_b}\n")
        
        # Add analysis for white
        for i in range(2, 6):
            open_w, semi_open_w = self.detect_rows(self.board, "w", i)
            self.white_analysis.insert(tk.END, f"Open rows of length {i}: {open_w}\n")
            self.white_analysis.insert(tk.END, f"Semi-open rows of length {i}: {semi_open_w}\n")

    # Game Logic Functions (from your original code)
    def make_empty_board(self, sz):
        board = []
        for i in range(sz):
            board.append([" "]*sz)
        return board
    
    def is_empty(self, board):
        for row in board:
            for cell in row:
                if cell != " ":
                    return False
        return True
    
    def is_bounded(self, board, y_end, x_end, length, d_y, d_x):
        y_start = y_end - (length - 1) * d_y
        x_start = x_end - (length - 1) * d_x

        y_before, x_before = y_start - d_y, x_start - d_x
        y_after, x_after = y_end + d_y, x_end + d_x

        def is_within_bounds(y, x):
            return 0 <= y < len(board) and 0 <= x < len(board[0])

        before_open = is_within_bounds(y_before, x_before) and board[y_before][x_before] == " "
        after_open = is_within_bounds(y_after, x_after) and board[y_after][x_after] == " "

        if before_open and after_open:
            return "OPEN"
        elif before_open or after_open:
            return "SEMIOPEN"
        else:
            return "CLOSED"
    
    def detect_row(self, board, col, y_start, x_start, length, d_y, d_x):
        open_seq_count, semi_open_seq_count = 0, 0
        y, x = y_start, x_start
        
        current_length = 0
        start_y, start_x = y, x

        while 0 <= y < len(board) and 0 <= x < len(board[0]):
            if board[y][x] == col:
                if current_length == 0:
                    start_y, start_x = y, x
                current_length += 1
            else:
                if current_length == length:
                    bound_type = self.is_bounded(board, start_y + (current_length-1)*d_y, 
                                            start_x + (current_length-1)*d_x, length, d_y, d_x)
                    if bound_type == "OPEN":
                        open_seq_count += 1
                    elif bound_type == "SEMIOPEN":
                        semi_open_seq_count += 1
                current_length = 0
                
            y += d_y
            x += d_x
            
        if current_length == length:
            bound_type = self.is_bounded(board, start_y + (current_length-1)*d_y, 
                                    start_x + (current_length-1)*d_x, length, d_y, d_x)
            if bound_type == "OPEN":
                open_seq_count += 1
            elif bound_type == "SEMIOPEN":
                semi_open_seq_count += 1

        return open_seq_count, semi_open_seq_count

    def detect_rows(self, board, col, length):
        open_seq_count, semi_open_seq_count = 0, 0

        # Check horizontal rows
        for y in range(len(board)):
            count_open, count_semi_open = self.detect_row(board, col, y, 0, length, 0, 1)
            open_seq_count += count_open
            semi_open_seq_count += count_semi_open

        # Check vertical rows
        for x in range(len(board[0])):
            count_open, count_semi_open = self.detect_row(board, col, 0, x, length, 1, 0)
            open_seq_count += count_open
            semi_open_seq_count += count_semi_open

        # Check diagonal rows (top-left to bottom-right)
        for y in range(len(board)):
            count_open, count_semi_open = self.detect_row(board, col, y, 0, length, 1, 1)
            open_seq_count += count_open
            semi_open_seq_count += count_semi_open
        for x in range(1, len(board[0])):
            count_open, count_semi_open = self.detect_row(board, col, 0, x, length, 1, 1)
            open_seq_count += count_open
            semi_open_seq_count += count_semi_open

        # Check diagonal rows (bottom-left to top-right)
        for y in range(len(board)):
            count_open, count_semi_open = self.detect_row(board, col, y, 0, length, -1, 1)
            open_seq_count += count_open
            semi_open_seq_count += count_semi_open
        for x in range(1, len(board[0])):
            count_open, count_semi_open = self.detect_row(board, col, len(board) - 1, x, length, -1, 1)
            open_seq_count += count_open
            semi_open_seq_count += count_semi_open

        return open_seq_count, semi_open_seq_count
        
    def search_max(self, board):
        best_score = float('-inf')
        move_y, move_x = -1, -1

        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] == " ":
                    board[y][x] = "b"
                    current_score = self.score(board)
                    board[y][x] = " "
                    if current_score > best_score:
                        best_score = current_score
                        move_y, move_x = y, x

        return move_y, move_x

    def score(self, board):
        MAX_SCORE = 100000
        
        open_b = {}
        semi_open_b = {}
        open_w = {}
        semi_open_w = {}
        
        for i in range(2, 6):
            open_b[i], semi_open_b[i] = self.detect_rows(board, "b", i)
            open_w[i], semi_open_w[i] = self.detect_rows(board, "w", i)
            
        if open_b[5] >= 1 or semi_open_b[5] >= 1:
            return MAX_SCORE
        
        elif open_w[5] >= 1 or semi_open_w[5] >= 1:
            return -MAX_SCORE
        
        if open_w[4] >= 1:
            return -MAX_SCORE + 1
            
        return (-10000 * (open_w[4] + semi_open_w[4])+ 
                500  * open_b[4]                     + 
                50   * semi_open_b[4]                + 
                -100  * open_w[3]                    + 
                -30   * semi_open_w[3]               + 
                50   * open_b[3]                     + 
                10   * semi_open_b[3]                +  
                open_b[2] + semi_open_b[2] - open_w[2] - semi_open_w[2])
        
    def is_win(self, board):
        for col in ["b", "w"]:
            if self.detect_rows(board, col, 5)[0] >= 1 or self.detect_rows(board, col, 5)[1] >= 1:
                return "Black won" if col == "b" else "White won"

        if all(cell != " " for row in board for cell in row):
            return "Draw"
        
        return "Continue"


def main():
    root = tk.Tk()
    game = GomokuGUI(root, board_size=8)
    root.mainloop()

if __name__ == "__main__":
    main()