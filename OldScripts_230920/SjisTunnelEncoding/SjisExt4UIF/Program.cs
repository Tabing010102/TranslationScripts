using System.Text;
using Yuka.Util;

namespace SjisExt4UIF
{
    internal class Program
    {
        static void Main(string[] args)
        {
            var u8WithoutBom = new UTF8Encoding(false);
            EncodingUtils.SetSjisMappingTable(args.Length >= 1 ? args[0] : "sjis_ext.bin");
            File.WriteAllText(args.Length >= 2 ? args[1] : "sjis_ext.txt", EncodingUtils.ShiftJisTunnelEncoding.CharTable, u8WithoutBom);
            var oriChars = new List<char>();
            var tunnelChars = new List<char>();
            foreach ((var k, var v) in EncodingUtils.ShiftJisTunnelEncoding.Mappings)
            {
                oriChars.Add(k);
                tunnelChars.Add(v);
            }
            File.WriteAllText(args.Length >= 3 ? args[2] : "sjis_ext_ori.txt", new string(oriChars.ToArray()), u8WithoutBom);
            File.WriteAllText(args.Length >= 4 ? args[3] : "sjis_ext_tunnel.txt", new string(tunnelChars.ToArray()), u8WithoutBom);
        }
    }
}
