/*
 * Copyright (c) 2024 Alexander Krassovsky
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// Note: GitHub username is save-buffer
module tt_um_save_buffer_streaming_hash (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

   reg [7:0] 	      hash;
   wire [7:0] 	      mix;
   assign mix = hash ^ ui_in;
   assign uo_out = hash;
   assign uio_oe[0] = 0;
   

   always @(posedge clk) begin
       if (!rst_n) begin
	   hash <= 8'h42;
       end
       else if (uio_in[0]) begin
	   hash <= mix ^ {mix[3:0], mix[7:4]};
       end
   end


  // All output pins must be assigned. If not used, assign to 0.
  assign uio_out = 0;
  assign uio_oe[7:1]  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule
