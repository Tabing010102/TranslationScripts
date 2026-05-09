using System.Text;
using System.Text.Json;
using UAssetAPI;
using UAssetAPI.UnrealTypes;
using UAssetAPI.Unversioned;

namespace BatchUAssetPacker;

internal static class Program
{
    private static readonly UTF8Encoding Utf8NoBom = new(false);
    private const EngineVersion GameEngineVersion = EngineVersion.VER_UE5_3;

    public static int Main(string[] args)
    {
        if (args.Length != 2 || (args[0] != "extract" && args[0] != "pack"))
        {
            Console.Error.WriteLine("Usage: BatchUAssetPacker <extract|pack> <config.json>");
            return 1;
        }

        try
        {
            var config = WorkflowConfig.Load(args[1]);
            return args[0] switch
            {
                "extract" => RunExtract(config),
                "pack" => RunPack(config),
                _ => 1,
            };
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            return 1;
        }
    }

    private static int RunExtract(WorkflowConfig config)
    {
        config.ValidateForExtract();

        var mappings = new Usmap(config.UsmapPath);
        var assetPaths = Directory
            .EnumerateFiles(config.UnpackedUAssetDir, "*.uasset", SearchOption.AllDirectories)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        if (assetPaths.Length == 0)
        {
            Console.Error.WriteLine($"No .uasset files found under '{config.UnpackedUAssetDir}'.");
            return 1;
        }

        Directory.CreateDirectory(config.ExportedJsonDir);

        var extractedCount = 0;
        var failedCount = 0;

        for (var index = 0; index < assetPaths.Length; index++)
        {
            var assetPath = assetPaths[index];
            var relativePath = Path.GetRelativePath(config.UnpackedUAssetDir, assetPath);
            var jsonPath = Path.Combine(config.ExportedJsonDir, Path.ChangeExtension(relativePath, ".json"));

            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(jsonPath)!);

                var asset = new UAsset(assetPath, GameEngineVersion, mappings);
                var json = asset.SerializeJson(true);
                File.WriteAllText(jsonPath, json, Utf8NoBom);

                extractedCount++;
                Console.WriteLine($"[{index + 1}/{assetPaths.Length}] Extracted {relativePath}");
            }
            catch (Exception ex)
            {
                failedCount++;
                Console.Error.WriteLine($"[extract] Failed: {relativePath} ({ex.Message})");
            }
        }

        Console.WriteLine($"Extracted {extractedCount} asset(s) to '{config.ExportedJsonDir}'. Failed: {failedCount}.");
        return failedCount == 0 ? 0 : 2;
    }

    private static int RunPack(WorkflowConfig config)
    {
        config.ValidateForPack();

        var mappings = new Usmap(config.UsmapPath);
        var jsonPaths = Directory
            .EnumerateFiles(config.ModifiedJsonDir, "*.json", SearchOption.AllDirectories)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        if (jsonPaths.Length == 0)
        {
            Console.Error.WriteLine($"No modified JSON files found under '{config.ModifiedJsonDir}'.");
            return 1;
        }

        Directory.CreateDirectory(config.RepackedUAssetDir);

        var packedCount = 0;
        var failedCount = 0;

        for (var index = 0; index < jsonPaths.Length; index++)
        {
            var jsonPath = jsonPaths[index];
            var relativePath = Path.GetRelativePath(config.ModifiedJsonDir, jsonPath);
            var assetPath = Path.Combine(config.RepackedUAssetDir, Path.ChangeExtension(relativePath, ".uasset"));
            var sourceAssetPath = Path.Combine(config.UnpackedUAssetDir, Path.ChangeExtension(relativePath, ".uasset"));

            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(assetPath)!);

                var json = File.ReadAllText(jsonPath, Utf8NoBom);
                var asset = UAsset.DeserializeJson(json);
                asset.Mappings = mappings;
                asset.FilePath = sourceAssetPath;
                asset.Write(assetPath);

                packedCount++;
                Console.WriteLine($"[{index + 1}/{jsonPaths.Length}] Packed {relativePath}");
            }
            catch (Exception ex)
            {
                failedCount++;
                Console.Error.WriteLine($"[pack] Failed: {relativePath} ({ex.Message})");
            }
        }

        Console.WriteLine($"Packed {packedCount} asset(s) to '{config.RepackedUAssetDir}'. Failed: {failedCount}.");
        return failedCount == 0 ? 0 : 2;
    }

    private sealed class WorkflowConfig
    {
        private WorkflowConfig(string configPath, string retocCliPath, string usmapPath, string gamePaksDir, string workspaceDir)
        {
            ConfigPath = configPath;
            RetocCliPath = retocCliPath;
            UsmapPath = usmapPath;
            GamePaksDir = gamePaksDir;
            WorkspaceDir = workspaceDir;
        }

        public string ConfigPath { get; }

        public string RetocCliPath { get; }

        public string UsmapPath { get; }

        public string GamePaksDir { get; }

        public string WorkspaceDir { get; }

        public string UnpackedUAssetDir => Path.Combine(WorkspaceDir, "1_UnpackedUAsset");

        public string ExportedJsonDir => Path.Combine(WorkspaceDir, "2_ExportedJson");

        public string ModifiedJsonDir => Path.Combine(WorkspaceDir, "3_ModifiedJson");

        public string RepackedUAssetDir => Path.Combine(WorkspaceDir, "4_RepackedUAsset");

        public static WorkflowConfig Load(string configPath)
        {
            var fullConfigPath = Path.GetFullPath(configPath);
            if (!File.Exists(fullConfigPath))
            {
                throw new FileNotFoundException($"Config file not found: {fullConfigPath}");
            }

            var configDirectory = Path.GetDirectoryName(fullConfigPath)!;
            var json = File.ReadAllText(fullConfigPath, Utf8NoBom);
            var rawConfig = JsonSerializer.Deserialize<RawConfig>(json) ?? throw new InvalidOperationException("Config file is empty.");

            var retocCliPath = ResolvePath(rawConfig.RetocCliPath, configDirectory, nameof(rawConfig.RetocCliPath));
            var usmapPath = ResolvePath(rawConfig.UsmapPath, configDirectory, nameof(rawConfig.UsmapPath));
            var gamePaksDir = ResolvePath(rawConfig.GamePaksDir, configDirectory, nameof(rawConfig.GamePaksDir));
            var workspaceDir = ResolvePath(rawConfig.WorkspaceDir, configDirectory, nameof(rawConfig.WorkspaceDir));

            return new WorkflowConfig(fullConfigPath, retocCliPath, usmapPath, gamePaksDir, workspaceDir);
        }

        public void ValidateForExtract()
        {
            ValidateFileExists(UsmapPath, nameof(UsmapPath));
            ValidateDirectoryExists(UnpackedUAssetDir, nameof(UnpackedUAssetDir));
        }

        public void ValidateForPack()
        {
            ValidateFileExists(UsmapPath, nameof(UsmapPath));
            ValidateDirectoryExists(ModifiedJsonDir, nameof(ModifiedJsonDir));
        }

        private static void ValidateFileExists(string path, string label)
        {
            if (!File.Exists(path))
            {
                throw new FileNotFoundException($"{label} does not exist: {path}");
            }
        }

        private static void ValidateDirectoryExists(string path, string label)
        {
            if (!Directory.Exists(path))
            {
                throw new DirectoryNotFoundException($"{label} does not exist: {path}");
            }
        }

        private static string ResolvePath(string? value, string baseDirectory, string fieldName)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                throw new InvalidOperationException($"Missing required config field: {fieldName}");
            }

            return Path.GetFullPath(Path.IsPathRooted(value) ? value : Path.Combine(baseDirectory, value));
        }

        private sealed class RawConfig
        {
            public string? RetocCliPath { get; set; }

            public string? UsmapPath { get; set; }

            public string? GamePaksDir { get; set; }

            public string? WorkspaceDir { get; set; }
        }
    }
}
