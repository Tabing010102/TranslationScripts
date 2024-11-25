using Newtonsoft.Json.Linq;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Unicode;

namespace SjisTunnelEncoding
{
    internal class Program
    {
        static void Main(string[] args)
        {
            var sjisTunnelEncoding = new Yuka.Utils.SjisTunnelEncoding();
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            var e932 = Encoding.GetEncoding(932);
            var u8WithoutBom = new UTF8Encoding(false);
            string contents = File.ReadAllText(args[0], u8WithoutBom);
            var data_dict = JsonSerializer.Deserialize<Dictionary<string, string>>(contents);
            var out_dict = new Dictionary<string, string>();
            foreach ((string k, string v) in data_dict)
            {
                var v2b = sjisTunnelEncoding.GetBytes(v);
                out_dict[Convert.ToBase64String(e932.GetBytes(k))] = Convert.ToBase64String(v2b);
            }
            var fs = File.OpenWrite(args[1]);
            var str = JsonSerializer.Serialize(out_dict, new JsonSerializerOptions
            {
                WriteIndented = true,
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            });
            fs.Write(u8WithoutBom.GetBytes(str));
            byte[] sjisExtContent = sjisTunnelEncoding.GetMappingTable();
            if (sjisExtContent.Length > 0)
                File.WriteAllBytes("sjis_ext.bin", sjisExtContent);
        }
    }
}
