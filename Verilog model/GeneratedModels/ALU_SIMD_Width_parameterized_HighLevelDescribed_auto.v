`timescale 1 ns / 100 ps  
module ALU_SIMD_Width_parameterized_HighLevelDescribed_auto(

		input [Width-1:0] W,
		input [Width-1:0] Z,
		input [Width-1:0] Y,
		input [Width-1:0] X,

		input [1:0] op,
		input Z_controller,
		input S_controller,
		input W_X_Y_controller,
		input [1:0] CIN_W_X_Y_CIN,
		input [1:0] CIN_Z_W_X_Y_CIN,

		output [Width-1:0] S,

		output [1:0] COUT_W_X_Y_CIN,
		output [1:0] COUT_Z_W_X_Y_CIN,

		input [0:0] result_SIDM_carry_in,
		output [0:0] result_SIDM_carry_out
	);

//parameters
parameter Width = 8;

// controllable not
wire [11:0] Z_Z_bar;
assign Z_Z_bar 	= Z ^ {Width{Z_controller}};

// logical part
wire [Width-1:0] out_and;
wire [Width-1:0] out_or;
wire [Width-1:0] out_xor;
assign out_and 	= X & Z_Z_bar;
assign out_or   = X | Z_Z_bar;
assign out_xor 	= X ^ Z_Z_bar ^ Y;

//computations
wire [Width-1:0] temp_W_X_Y;
assign {{COUT_W_X_Y_CIN}, {temp_W_X_Y}} = W + X + Y + CIN_W_X_Y_CIN;

wire [Width-1:0] temp_W_X_Y_xored;
assign temp_W_X_Y_xored = {12{W_X_Y_controller}} ^  temp_W_X_Y;

wire [Width-1:0] S_temp_sum;
assign {{COUT_Z_W_X_Y_CIN},{S_temp_sum}} = temp_W_X_Y_xored + Z_Z_bar + CIN_Z_W_X_Y_CIN;

assign result_SIDM_carry_out = result_SIDM_carry_in + COUT_W_X_Y_CIN + COUT_Z_W_X_Y_CIN;

reg [Width-1:0] S_temp_selected;

always@(*)begin
	case (op)
		2'b00: S_temp_selected = S_temp_sum;
		2'b01: S_temp_selected = out_xor;
		2'b10: S_temp_selected = out_and;
		2'b11: S_temp_selected = out_or;
	endcase
end

assign S = S_temp_selected ^ {Width{S_controller}};

endmodule
