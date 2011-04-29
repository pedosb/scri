import java.util.Vector;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.lang.Double;
import java.lang.Math;

class EndOfFile extends Exception{
}
class NoSensorInput extends Exception{
}

public class Main{

	private Vector<Double[]> sensors_value;
	private Vector<Double> tempS;

	private BufferedReader br;
	private static int N_SENSORS = 2;

	public Main(BufferedReader br){
		sensors_value = new Vector<Double[]>();
		tempS = new Vector<Double>();
		this.br = br; 
	}

	public static void main(String[] args){
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		double flow;
		try {
			while (true){
				Main m = new Main(br);
				try{
					while (true){
						m.readSensors();
						flow = m.get_flow();
						if (flow < 0)
							flow = 0;
						else if (flow > 1000)
							flow = 1000;
						System.out.println(flow);
//						m.get_flow();
					}
				} catch (NoSensorInput e){
					System.out.println("fail");
				}catch (IOException e){
					System.out.println(e);
				}
			}
		} catch (EndOfFile e){
		}
	}

	private void readSensors() throws IOException, EndOfFile, NoSensorInput{
		Double[] sensors_read = new Double[N_SENSORS];
		Double read_value = null;
		String value;
		int i;
		for (i = 0; i < N_SENSORS; i++){
			value = br.readLine();
			if (value == null){
				throw new EndOfFile();
			}
			String[] value_s = value.trim().split(" ");
			if (value_s.length != 2)
				sensors_read[i] = null;
			else
				read_value = Double.valueOf(value_s[1].replace(",","."));
				if (read_value == null || read_value < 0 || read_value > 10)
					sensors_read[i] = null;
				else
					sensors_read[i] = read_value;
		}
		sensors_value.add(sensors_read);
		tempS.add(voltsToTemperature(getTs(sensors_read[0], sensors_read[1])));
	}

	private double getTs(Double t1, Double t2) throws NoSensorInput{
		if (t1 == null && t2 == null)
			throw new NoSensorInput();
		if (t1 == null)
			return t2;
		if (t2 == null)
			return t1;
		double p1 = 0.978,
			  p2 = 1.013;
		return (t1 * p1 + t2 * p2) / (p1+p2);
	}

	private double voltsToTemperature(double v){
		Double w = 456.0,
			   y = 0.104,
			   z = 0.01,
			   k = 5.21;
		return -w * Math.log(1 - (v * y - z) / k);
	}

	private double get_flow(){
		int size = tempS.size();
		double[] eS = new double[size],
				 x = new double[size];
		double kc = 0.0495,
			   ti = 11.7;
		for (int i = 0; i < size; i++){
			eS[i] = tempS.get(i) - 45;
			x[i] = i;
		}
		double e = eS[size-1];
//		System.out.println(Trapezoid.trapezoidRule(size, x, eS));
//		for (int i = 0; i < size; i++){
//			System.out.print(eS[i] + " ");
//		}
//		System.out.println();
		return 250.0 * kc * (e + Trapezoid.trapezoidRule(size, x, eS) / ti);
	}

	private Object[] parseSensor(int sensor, String value){
		Object[] result = {1,2};
		return result;
	}
}
/**
 * Trapezoid-rule integration of a set of data points NOT evenly
 * spaced along the X-axis.  They _are_ assumed to be ordered along
 * that axis.
 *
 * Input file:
 *   Number of data points
 *   Followed by that number of white-space delimited x y pairs
 *
 * No data validation is done --- the file is presumed valid.
 *
 * Language:  Java version 5.0 [uses Scanner and printf]
 *
 * Author:  Timothy Rolfe
 *
 * From: http://penguin.ewu.edu/cscd543/Spr-2009/NumInt/NumInt.html
 */
/*
import java.io.*;
import java.util.Scanner;
*/

class Trapezoid
{
   static double trapezoidRule (int size, double[] x, double[] y)
   {
      double sum = 0.0,
             increment;

      for ( int k = 1; k < size; k++ )
      {//Trapezoid rule:  1/2 h * (f0 + f1)
         increment = 0.5 * (x[k]-x[k-1]) * (y[k]+y[k-1]);
         sum += increment;
      }
      return sum;
   }

/*
   public static void main ( String[] args ) throws Exception
   {
      String   fileName = args.length > 0 ? args[0] : "InpData.txt";
      Scanner  inp = new Scanner(new File(fileName));
      int      k, size;
      double[] x, y;
      double   integral;

      size = inp.nextInt();
      System.out.println ("Number of points:  " + size);

      x = new double[size];
      y = new double[size];

      for ( k = 0; k < size; k++ )
      {
         x[k] = inp.nextDouble();
         y[k] = inp.nextDouble();
      }
      integral = trapezoidRule (size, x, y);
      System.out.printf ("Integral:  %8.8f\n", integral);
      System.out.printf ("Check:  log(%2.2f) = %8.8f\n",
                         x[size-1], Math.log(x[size-1]) );
   }
*/
}
