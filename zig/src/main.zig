const std = @import("std");
pub fn main() !void {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);
    if (args.len != 2) {
        std.debug.print("Usage: mcctl <status|logs|players|restart|backup>\n", .{});
        return;
    }
    const command = args[1];
    const cmd: []const []const u8 = if (std.mem.eql(u8, command, "status"))
        &.{ "docker", "compose", "ps" }
    else if (std.mem.eql(u8, command, "logs"))
        &.{ "docker", "compose", "logs", "--tail=80", "minecraft" }
    else if (std.mem.eql(u8, command, "players"))
        &.{ "docker", "compose", "exec", "-T", "minecraft", "rcon-cli", "list" }
    else if (std.mem.eql(u8, command, "restart"))
        &.{ "docker", "compose", "restart", "minecraft" }
    else if (std.mem.eql(u8, command, "backup"))
        &.{ "bash", "scripts/backup.sh" }
    else {
        std.debug.print("Unknown command\n", .{});
        return;
    };
    var child = std.process.Child.init(cmd, allocator);
    child.stdin_behavior = .Inherit;
    child.stdout_behavior = .Inherit;
    child.stderr_behavior = .Inherit;
    const result = try child.spawnAndWait();
    switch (result) {
        .Exited => |code| {
            if (code != 0) return error.CommandFailed;
        },
        else => return error.CommandFailed,
    }
}
